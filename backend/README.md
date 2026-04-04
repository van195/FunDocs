# FunDocs — Backend

Django REST API for **authentication**, **Chapa payments**, **document upload & processing**, **RAG-backed chat**, and **quizzes**. All application routes are mounted under **`/api/`**.

---

## Table of contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Run](#run)

- [API reference](#api-reference)

- [RAG & embeddings](#rag--embeddings)


---

## Requirements

- Python **3.10+**
- Dependencies listed in [`requirements.txt`](requirements.txt) (Django 5, DRF, SimpleJWT, PyMuPDF, scikit-learn, etc.)

---

## Setup

```bash
cd backend

pip install -r requirements.txt
```

Copy the environment template and fill in real values:

```bash
cp .env.example .env    
```

Apply migrations:

```bash
python manage.py migrate
```

Optional: create a superuser for the Django admin (`/admin/`):

```bash
python manage.py createsuperuser
```

---

## Run

```bash
python manage.py runserver
```

- API root: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`
- Uploaded files and generated RAG artifacts: under `MEDIA_ROOT` (default `media/`)

---

## Environment variables

Defined in [`.env.example`](.env.example). Summary:

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django secret; **required** in production. |
| `DJANGO_DEBUG` | `1` / `0` — when `1` and `CORS_ALLOW_ORIGINS` is empty, all origins are allowed (dev convenience). |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames. |
| `CORS_ALLOW_ORIGINS` | Comma-separated frontend origins (e.g. `http://localhost:5173`). |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Access token lifetime. |
| `MEDIA_ROOT` | Directory for uploads and RAG data (relative to `backend/` or absolute). |
| `CHAPA_PUBLIC_KEY`, `CHAPA_SECRET_KEY` | Chapa API credentials. |
| `CHAPA_BASE_URL` | Initialize endpoint (default Chapa URL). |
| `CHAPA_CALLBACK_URL` | Server webhook URL Chapa calls (must be reachable in production). |
| `CHAPA_RETURN_URL` | Browser redirect after checkout (usually your frontend). |
| `CHAPA_AMOUNT`, `CHAPA_CURRENCY` | Default payment amount and currency. |
| `GROQ_API_KEY` | Groq API key for chat (and embeddings if enabled). |
| `GROQ_CHAT_MODEL` | Chat model id (see [Groq docs](https://console.groq.com/docs/models)). |
| `EMBEDDINGS_BACKEND` | `local` (TF-IDF, default) or `groq`. |
| `GROQ_EMBED_MODEL` | Used when `EMBEDDINGS_BACKEND=groq`. |

---



### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/auth/register/` | Public | Create user + profile. Body: `username`, `email`, `password`. |
| `POST` | `/api/auth/login/` | Public | JWT pair. Body: `username`, `password`. |
| `POST` | `/api/auth/refresh/` | Public | New access token. Body: `refresh` (refresh token). |

### User & preferences

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/me/` | Current user profile: `has_access`, `fun_mode`, etc. |
| `PATCH` | `/api/me/preferences/` | Partial update; e.g. `{ "fun_mode": true }`. |

### Payments (Chapa)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/payments/chapa/create/` | User | Starts payment; returns `authorization_url`, `tx_ref`. User must have `email`. |
| `POST` | `/api/payments/chapa/callback/` | **Public** (webhook) | Chapa server-to-server callback; may set `has_access` on success. CSRF exempt. |
| `POST` | `/api/payments/chapa/verify-latest/` | User | Verifies latest pending payment with Chapa; updates access. |

### Documents

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/documents/upload/` | Paid | Multipart field `file`. Allowed: `.pdf`, `.txt`, `.docx`. Processes synchronously. |
| `GET` | `/api/documents/` | Paid | List current user’s documents and processing status. |

### Chat

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/chat/ask/` | Paid | Body: `{ "document_id": <int>, "question": "<string>" }`. Uses RAG + Groq; respects `fun_mode`. |

### Quiz

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/quiz/generate/` | Paid | Body: `{ "document_id": <int>, "num_questions": 3–10 }` (optional, default 5). Returns `quiz_id` and questions **without** correct answers. |
| `POST` | `/api/quiz/submit/` | Paid | Body: `{ "quiz_id": <int>, "answers": [ { "question_id": "<str>", "selected_index": 0–3 }, ... ] }` — one entry per question. Returns score, percentage, and explanations. |
| `GET` | `/api/quiz/history/?document_id=<int>` | Paid | Recent submitted attempts for the user (optional filter by document). |

**Paid routes** require `UserProfile.has_access == True` (enforced by `IsPaid` permission).

### Typical JSON responses

- **Errors**: `{ "detail": "..." }` or `{ "detail": "...", "error": "..." }` depending on the view.  
- **Chat**: `{ "answer": "<string>" }`.  
- **Quiz generate**: `{ "quiz_id", "document_id", "questions": [ { "id", "question", "options" } ] }`.  
- **Quiz submit**: `{ "quiz_id", "score", "max_score", "percentage", "results": [ ... ] }` where each result includes correctness and `explanation`.  

---

## Data model (overview)

| Model | Role |
|-------|------|
| `User` | Django auth user; registration requires `email` for Chapa. |
| `UserProfile` | `has_access`, `fun_mode`, optional `chapa_email`. |
| `ChapaPayment` | Transaction metadata and status. |
| `UploadedDocument` | File, processing status, paths to RAG artifacts. |
| `QuizAttempt` | Generated questions (server stores `correct_index`), optional submission, score, explanations. |

Inspect and edit records in **Django admin** after `createsuperuser`.

---

## RAG & embeddings

1. **Extract** text (PyMuPDF / UTF-8 / python-docx).  
2. **Chunk** with overlap; persist `chunks.json` under `MEDIA_ROOT/rag/user_<id>/doc_<id>/`.  
3. **Index**  
   - **`local`**: TF-IDF + L2-normalized sparse matrix (scikit-learn).  
   - **`groq`**: embedding vectors via Groq OpenAI-compatible embeddings API.  
4. **Query**: embed or vectorize the user question, cosine similarity, top‑k chunks passed to Groq chat.

Quiz generation uses the same retrieval step to ground MCQs in document content; explanations use retrieved context and the user’s **`fun_mode`** flag.

---

## Troubleshooting

| Symptom | Things to check |
|---------|------------------|
| CORS errors from the browser | `CORS_ALLOW_ORIGINS` matches the frontend origin exactly (scheme + host + port). |
| `Missing GROQ_API_KEY` | Set in `backend/.env` and restart the server. |
| Chapa initialize fails | `CHAPA_PUBLIC_KEY`, `CHAPA_SECRET_KEY`, and public `callback` URL. |
| Document stuck in `pending` / `error` | Response body may include `processing_error`; PDFs with only images may yield little text. |
| Quiz JSON errors | Model must return a parseable JSON **array**; retries or adjusting `GROQ_CHAT_MODEL` may help. |

For full-stack setup, see the [project README](../README.md).
