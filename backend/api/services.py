import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import requests
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from scipy import sparse

from .models import UploadedDocument


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


def file_ext(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())
    return ext


def validate_extension(filename: str) -> None:
    ext = file_ext(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {sorted(ALLOWED_EXTENSIONS)}")


def extract_text_from_file(doc: UploadedDocument) -> str:
    
    validate_extension(doc.original_filename)
    path = doc.file.path
    ext = file_ext(doc.original_filename)

    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if ext == ".pdf":
        # NOTE: PDF extraction can be messy. PyMuPDF is generally robust.
        pdf = fitz.open(path)
        parts: List[str] = []
        for page in pdf:
            parts.append(page.get_text("text"))
        return "\n".join(parts)

    if ext == ".docx":
        d = DocxDocument(path)
        parts = [p.text for p in d.paragraphs if p.text and p.text.strip()]
        return "\n".join(parts)

    raise ValueError("Unsupported file type")


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    
    text = normalize_whitespace(text)
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(0, end - overlap)
    return chunks


def cos_sim_topk(
    query_vec: np.ndarray, mat: np.ndarray, top_k: int = 6
) -> List[Tuple[int, float]]:
    
    sims = mat @ query_vec  # cosine similarity due to normalization
    if top_k >= len(sims):
        idxs = np.argsort(-sims)
    else:
        idxs = np.argpartition(-sims, top_k)[:top_k]
        idxs = idxs[np.argsort(-sims[idxs])]
    return [(int(i), float(sims[i])) for i in idxs]


def groq_headers() -> Dict[str, str]:
    api_key = os.environ.get("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", None)
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY")
    return {"Authorization": f"Bearer {api_key}"}


def groq_embed_model() -> str:
    return os.environ.get("GROQ_EMBED_MODEL", "nomic-embed-text-v1")


def groq_chat_model() -> str:
    # Default: Groq-supported model (llama3-70b-8192 was decommissioned).
    return os.environ.get("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")


def groq_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Groq OpenAI-compatible embeddings endpoint.
    """
    url = "https://api.groq.com/openai/v1/embeddings"
    headers = groq_headers()
    payload = {"model": groq_embed_model(), "input": texts}
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return [item["embedding"] for item in data["data"]]


def groq_chat(messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    """
    Groq OpenAI-compatible chat completions endpoint.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = groq_headers()
    payload = {
        "model": groq_chat_model(),
        "messages": messages,
        "temperature": temperature,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=180)
    if not resp.ok:
        # Bubble up Groq's error payload for debugging.
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Groq chat error {resp.status_code}: {detail}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def rag_dir_for_doc(doc: UploadedDocument) -> str:
    return os.path.join(settings.MEDIA_ROOT, "rag", f"user_{doc.user_id}", f"doc_{doc.id}")


def embeddings_backend() -> str:
    return os.environ.get("EMBEDDINGS_BACKEND", "local").strip().lower()


def save_local_tfidf(doc: UploadedDocument, chunks: List[str]) -> None:
    base_dir = rag_dir_for_doc(doc)
    os.makedirs(base_dir, exist_ok=True)

    vectorizer = TfidfVectorizer(max_features=50000)
    mat = vectorizer.fit_transform(chunks)
    mat = normalize(mat, norm="l2", axis=1, copy=False)

    sparse.save_npz(os.path.join(base_dir, "tfidf.npz"), mat)
    with open(os.path.join(base_dir, "tfidf_vocab.json"), "w", encoding="utf-8") as f:
        # Store minimal vectorizer state
        vocab = {k: int(v) for k, v in (vectorizer.vocabulary_ or {}).items()}
        json.dump(
            {
                "vocabulary_": vocab,
                "idf_": vectorizer.idf_.tolist(),
            },
            f,
            ensure_ascii=False,
        )


def load_local_tfidf(doc: UploadedDocument):
    base_dir = rag_dir_for_doc(doc)
    mat = sparse.load_npz(os.path.join(base_dir, "tfidf.npz"))
    with open(os.path.join(base_dir, "tfidf_vocab.json"), "r", encoding="utf-8") as f:
        state = json.load(f)
    vectorizer = TfidfVectorizer(max_features=50000)
    vectorizer.vocabulary_ = {k: int(v) for k, v in state["vocabulary_"].items()}
    vectorizer.idf_ = np.array(state["idf_"], dtype=np.float64)
    vectorizer._tfidf._idf_diag = sparse.spdiags(vectorizer.idf_, diags=0, m=len(vectorizer.idf_), n=len(vectorizer.idf_))
    return vectorizer, mat


def save_rag_artifacts(doc: UploadedDocument, chunks: List[str]) -> None:
    
    if not chunks:
        raise ValueError("No text chunks to embed.")

    os.makedirs(rag_dir_for_doc(doc), exist_ok=True)

    base_dir = rag_dir_for_doc(doc)
    os.makedirs(base_dir, exist_ok=True)

    backend = embeddings_backend()
    if backend == "groq":
        embeddings = groq_embeddings(chunks)
        mat = np.array(embeddings, dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        mat = mat / norms
        np.save(os.path.join(base_dir, "embeddings.npy"), mat)
        with open(os.path.join(base_dir, "embeddings_backend.json"), "w", encoding="utf-8") as f:
            json.dump({"backend": "groq"}, f)
    else:
        save_local_tfidf(doc, chunks)
        with open(os.path.join(base_dir, "embeddings_backend.json"), "w", encoding="utf-8") as f:
            json.dump({"backend": "local"}, f)

    with open(os.path.join(rag_dir_for_doc(doc), "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)


def load_rag_artifacts(doc: UploadedDocument) -> Tuple[np.ndarray, List[str]]:
    base_dir = rag_dir_for_doc(doc)
    chunks_path = os.path.join(base_dir, "chunks.json")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    backend_path = os.path.join(base_dir, "embeddings_backend.json")
    backend = "groq"
    if os.path.exists(backend_path):
        with open(backend_path, "r", encoding="utf-8") as bf:
            backend = (json.load(bf) or {}).get("backend", "groq")

    if backend == "local":
        vectorizer, mat = load_local_tfidf(doc)
        return (vectorizer, mat), chunks

    emb_path = os.path.join(base_dir, "embeddings.npy")
    mat = np.load(emb_path)
    return mat, chunks


def get_rag_context_for_query(*, doc: UploadedDocument, query: str, top_k: int = 8) -> str:
    emb_obj, chunks = load_rag_artifacts(doc)
    if isinstance(emb_obj, tuple):
        vectorizer, mat = emb_obj
        q = vectorizer.transform([query])
        q = normalize(q, norm="l2", axis=1, copy=False)
        sims = (mat @ q.T).toarray().ravel()
        idxs = np.argsort(-sims)[:top_k]
        scored = [(int(i), float(sims[i])) for i in idxs]
    else:
        mat = emb_obj
        q_emb = groq_embeddings([query])[0]
        q_vec = np.array(q_emb, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            q_norm = 1.0
        q_vec = q_vec / q_norm
        scored = cos_sim_topk(q_vec, mat, top_k=top_k)
    return build_context(chunks, scored, max_chunks=top_k)


def extract_json_array(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON array found in model output.")
    return json.loads(text[start : end + 1])


def normalize_quiz_questions(raw: Any, *, expected_count: int) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        raise ValueError("Quiz model returned non-list JSON.")
    if len(raw) != expected_count:
        raise ValueError(f"Expected {expected_count} questions, got {len(raw)}.")
    out: List[Dict[str, Any]] = []
    for i, q in enumerate(raw):
        if not isinstance(q, dict):
            raise ValueError("Each question must be an object.")
        qid = str(q.get("id") or f"q{i + 1}")
        question = (q.get("question") or "").strip()
        options = q.get("options")
        if not isinstance(options, list) or len(options) != 4:
            raise ValueError(f"Question {qid} must have exactly 4 options.")
        options = [str(o).strip() for o in options]
        if any(not o for o in options):
            raise ValueError(f"Question {qid} has empty options.")
        try:
            ci = int(q.get("correct_index"))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Question {qid} needs integer correct_index.") from e
        if ci not in (0, 1, 2, 3):
            raise ValueError(f"Question {qid}: correct_index must be 0-3.")
        if not question:
            raise ValueError(f"Question {qid} has empty text.")
        out.append(
            {
                "id": qid,
                "question": question,
                "options": options,
                "correct_index": ci,
            }
        )
    return out


def generate_quiz_questions(*, doc: UploadedDocument, num_questions: int) -> List[Dict[str, Any]]:
    rq = (
        "Key concepts, definitions, facts, dates, names, and important details "
        "that could be tested with multiple-choice questions."
    )
    context = get_rag_context_for_query(doc=doc, query=rq, top_k=10)
    system = (
        "You create clear multiple-choice quiz questions for studying. "
        "Use ONLY the provided document context. If context is thin, ask simpler factual questions. "
        "Respond with ONLY a JSON array (no markdown, no commentary)."
    )
    user = (
        f"Create exactly {num_questions} multiple-choice questions.\n"
        "Each element must be a JSON object with: "
        '"id" (short string), "question" (string), '
        '"options" (array of exactly 4 distinct strings), '
        '"correct_index" (integer 0-3 pointing to the correct option).\n'
        "Vary difficulty. Do not repeat the same wording.\n\n"
        f"Document context:\n{context}"
    )
    raw_text = groq_chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.35,
    )
    parsed = extract_json_array(raw_text)
    return normalize_quiz_questions(parsed, expected_count=num_questions)


def explain_quiz_results(
    *,
    doc: UploadedDocument,
    questions: List[Dict[str, Any]],
    answer_by_qid: Dict[str, int],
    fun_mode: bool,
) -> List[Dict[str, str]]:
    context = get_rag_context_for_query(
        doc=doc,
        query="Evidence and quotes supporting quiz answers and explanations.",
        top_k=8,
    )
    lines: List[str] = []
    for q in questions:
        qid = q["id"]
        sel = answer_by_qid.get(qid, -1)
        correct_idx = q["correct_index"]
        opts = q["options"]
        correct_text = opts[correct_idx] if 0 <= correct_idx < len(opts) else ""
        picked = opts[sel] if 0 <= sel < len(opts) else "(no answer)"
        ok = sel == correct_idx
        lines.append(
            f"- id={qid}\n"
            f"  Q: {q['question']}\n"
            f"  User picked: {picked}\n"
            f"  Correct: {correct_text}\n"
            f"  User was {'CORRECT' if ok else 'WRONG'}."
        )
    block = "\n".join(lines)
    if fun_mode:
        system = (
            "You are a playful tutor. For EACH quiz item, write a short, memorable explanation "
            "of why the correct answer is right (and if the user was wrong, gently correct them). "
            "Use vivid analogies; you may sprinkle Amharic words or light Ethiopian-flavored humor. "
            "Stay grounded in the document context. "
            "Return ONLY JSON: an array of objects with keys question_id (string), explanation (string)."
        )
    else:
        system = (
            "For EACH quiz item, write a concise, accurate explanation referencing the document. "
            "Return ONLY JSON: an array of objects with keys question_id (string), explanation (string)."
        )
    user = (
        "Document context (for grounding):\n"
        f"{context}\n\n"
        "Quiz review items:\n"
        f"{block}\n\n"
        "Produce one explanation per question_id in the same order as listed."
    )
    raw_text = groq_chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4 if fun_mode else 0.2,
    )
    parsed = extract_json_array(raw_text)
    if not isinstance(parsed, list):
        raise ValueError("Explanations model returned non-list JSON.")
    out: List[Dict[str, str]] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        qid = str(item.get("question_id") or item.get("id") or "")
        expl = str(item.get("explanation") or "").strip()
        if qid and expl:
            out.append({"question_id": qid, "explanation": expl})
    return out


def build_context(chunks: List[str], scored: List[Tuple[int, float]], max_chunks: int = 6) -> str:
    selected = scored[:max_chunks]
    blocks: List[str] = []
    for rank, (idx, score) in enumerate(selected, start=1):
        snippet = chunks[idx].strip()
        blocks.append(f"### Context chunk {rank} (score={score:.3f})\n{snippet}")
    return "\n\n".join(blocks)


def is_explain_request(question: str) -> bool:
    q = question.strip().lower()
    patterns = [
        r"^explain\b",
        r"explain (this|the) (document|file|text)",
        r"summarize\b",
        r"give me (a )?summary\b",
        r"what is this\b",
        r"teach me\b",
    ]
    return any(re.search(p, q) for p in patterns)


def ask_groq_about_doc(
    *,
    doc: UploadedDocument,
    question: str,
    fun_mode: bool,
    top_k: int = 6,
) -> str:
    emb_obj, chunks = load_rag_artifacts(doc)

    if isinstance(emb_obj, tuple):
        # Local TF-IDF path
        vectorizer, mat = emb_obj
        q = vectorizer.transform([question])
        q = normalize(q, norm="l2", axis=1, copy=False)
        sims = (mat @ q.T).toarray().ravel()
        idxs = np.argsort(-sims)[:top_k]
        scored = [(int(i), float(sims[i])) for i in idxs]
        context = build_context(chunks, scored, max_chunks=top_k)
    else:
        mat = emb_obj
        # Groq embeddings path
        q_emb = groq_embeddings([question])[0]
        q_vec = np.array(q_emb, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            q_norm = 1.0
        q_vec = q_vec / q_norm
        scored = cos_sim_topk(q_vec, mat, top_k=top_k)
        context = build_context(chunks, scored, max_chunks=top_k)

    if fun_mode:
        system = (
            "Explain in a way I will never forget. Turn it into a [FORMAT: story/song/comedy sketch/gamified story]. Make it [TONE: hilarious/absurd/dramatic]. Include vivid imagery, unexpected twists, and make each key idea stick in my memory."
            "include amharic words and ethiopian based jokes and references"
            "explain like you are explaining to a donkey."
            "You are a friendly, funny tutor. Explain the document like you're teaching "
            "a child. Make it easy to remember, with playful analogies and short sentences. "
            "Use ONLY the provided context chunks. If the context doesn't contain the answer, say "
            "you don't know based on the text and ask what part to focus on.\n\n"
            "When helpful, use:\n"
            "- A simple analogy\n"
            "- A 3-step 'story' explanation\n"
        )
    else:
        system = (
            "You are a helpful assistant answering questions using only the provided document context. "
            "Be accurate, concise, and explain clearly. If the answer is not in the context, say so.\n\n"
            "If the user asks to explain or summarize, provide a structured summary first, then answer the question."
        )

    if is_explain_request(question):
        user_instruction = (
            "Explain the document to me. First provide a short summary, then explain the key points. "
            "After that, answer any implied questions.\n\n"
            f"Question: {question}"
        )
    else:
        user_instruction = f"Question: {question}"

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                "Use this document context to answer.\n\n"
                f"{context}\n\n"
                f"{user_instruction}"
            ),
        },
    ]

    return groq_chat(messages, temperature=0.2)


def chapa_initialize_payment(*, user, tx_ref: str) -> Dict[str, Any]:
    base_url = os.environ.get("CHAPA_BASE_URL", "https://api.chapa.co/v1/transaction/initialize")
    chapa_secret_key = os.environ.get("CHAPA_SECRET_KEY")
    public_key = os.environ.get("CHAPA_PUBLIC_KEY")
    if not chapa_secret_key or not public_key:
        raise RuntimeError("Missing CHAPA_PUBLIC_KEY or CHAPA_SECRET_KEY in env.")

    amount = os.environ.get("CHAPA_AMOUNT", "10")
    currency = os.environ.get("CHAPA_CURRENCY", "USD")
    callback_url = os.environ.get(
        "CHAPA_CALLBACK_URL", "http://localhost:8000/api/payments/chapa/callback/"
    )
    return_url = os.environ.get("CHAPA_RETURN_URL", "http://localhost:5173/")

    payload = {
        "amount": str(amount),
        "currency": currency,
        "email": user.email or "",
        "first_name": user.username or "",
        "tx_ref": tx_ref,
        "callback_url": callback_url,
        "return_url": return_url,
        "public_key": public_key,
    }
    headers = {"Authorization": f"Bearer {chapa_secret_key}"}

    resp = requests.post(base_url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Chapa's response fields have changed across examples; support multiple keys.
    auth_url = (
        (data.get("data") or {}).get("authorization_url")
        or (data.get("data") or {}).get("checkout_url")
        or data.get("authorization_url")
        or data.get("checkout_url")
    )

    return {"chapa_response": data, "authorization_url": auth_url}


def chapa_verify_payment(*, tx_ref: str) -> Dict[str, Any]:
    """
    Verifies a transaction status with Chapa.
    """
    chapa_secret_key = os.environ.get("CHAPA_SECRET_KEY")
    if not chapa_secret_key:
        raise RuntimeError("Missing CHAPA_SECRET_KEY in env.")

    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {"Authorization": f"Bearer {chapa_secret_key}"}
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Normalize status best-effort
    status_val = (data.get("data") or {}).get("status") or data.get("status") or ""
    status_norm = str(status_val).lower()
    if "success" in status_norm:
        status_norm = "success"
    return {"verify_response": data, "status": status_norm}


def parse_chapa_callback_payload(payload: Any) -> Tuple[str, str]:
    """
    Returns (tx_ref, status).
    """
    if not isinstance(payload, dict):
        payload = {}
    tx_ref = payload.get("tx_ref") or payload.get("txRef") or payload.get("reference") or ""
    status = payload.get("status") or payload.get("payment_status") or payload.get("event") or ""
    # Normalize success strings
    status_norm = str(status).lower()
    if "success" in status_norm:
        status_norm = "success"
    elif status_norm:
        status_norm = status_norm
    else:
        status_norm = "unknown"
    return str(tx_ref), str(status_norm)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)

