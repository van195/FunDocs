import { useCallback, useEffect, useMemo, useState } from "react";
import { apiFetch } from "../../api";

export default function QuizSection({ documentId, funMode }) {
  const [numQuestions, setNumQuestions] = useState(5);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [quizId, setQuizId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [selections, setSelections] = useState({});
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [someone,setSomeOne] = useState(false)
  console.log(history);
  
  const loadHistory = useCallback(async () => {
    setSomeOne(true)
    if (!documentId) {
      setHistory([]);
      return;
    }
    try {
      const path =
        `/quiz/history/?document_id=${encodeURIComponent(String(documentId))}`;
      const data = await apiFetch(path);
      setHistory(data.attempts || []);
    } catch {
      setHistory([]);
    }
  }, [documentId]);

  useEffect(() => {
    setQuizId(null);
    setQuestions([]);
    setSelections({});
    setResults(null);
    setError("");
    loadHistory();
  }, [documentId, loadHistory]);

  const allAnswered = useMemo(() => {
    if (!questions.length) return false;
    return questions.every((q) => selections[q.id] !== undefined && selections[q.id] !== null);
  }, [questions, selections]);

  async function generateQuiz() {
    if (!documentId) return;
    setError("");
    setBusy(true);
    setResults(null);
    try {
      const res = await apiFetch("/quiz/generate/", {
        method:  "POST",
        body: { document_id: documentId, num_questions: numQuestions }
      });
      setQuizId(res.quiz_id);
      setQuestions(res.questions || []);
      setSelections({});
    } catch (e) {
      setError(e.message || "Could not generate quiz");
      setQuizId(null);
      setQuestions([]);
    } finally {
      setBusy(false);
    }
  }

  async function submitQuiz() {
    if (!quizId || !allAnswered) return;
    setError("");
    setBusy(true);
    try {
      const answers = questions.map((q) => ({
        question_id: q.id,
        selected_index: selections[q.id]
      }));
      const res = await apiFetch("/quiz/submit/", {
        method: "POST",
        body: { quiz_id: quizId, answers }
      });
      setResults(res);
      await loadHistory();
    } catch (e) {
      setError(e.message || "Submit failed");
    } finally {
      setBusy(false);
    }
  }

  function resetQuiz() {
    setQuizId(null);
    setQuestions([]);
    setSelections({});
    setResults(null);
    setError("");
  }

  return (
    <div className="quizSection card">
      <div className="cardHeader">Quiz from your file</div>
      <p className="hint quizHint">
        The AI builds multiple-choice questions from the active document. After you submit, you get a
        score and short explanations for each question
        {funMode ? " (Fun Mode is on — explanations will match your playful setting)." : "."}
      </p>

      {!documentId ? (
        <div className="hint">Select a processed document to start a quiz.</div>
      ) : (
        <>
          <div className="quizToolbar">
            <label className="quizNumLabel">
              Questions
              <select
                value={numQuestions}
                disabled={busy || (questions.length > 0 && !results)}
                onChange={(e) => setNumQuestions(Number(e.target.value))}
              >
                {[3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              disabled={busy || (questions.length > 0 && !results)}
              onClick={generateQuiz}
            >
              {busy && !questions.length ? "Generating…" : "Generate quiz"}
            </button>
            {(questions.length > 0 || results) && (
              <button type="button" className="secondary" disabled={busy} onClick={resetQuiz}>
                Clear quiz
              </button>
            )}
          </div>
          {error ? <div className="error">{error}</div> : null}

          {results ? (
            <div className="quizResults">
              <div className="quizScoreBanner">
                Score: <strong>{results.score}</strong> / {results.max_score} ({results.percentage}%)
              </div>
              <ul className="quizResultList">
                {results.results.map((r) => (
                  <li key={r.question_id} className={`quizResultItem ${r.correct ? "ok" : "bad"}`}>
                    <div className="quizQtext">{r.question}</div>
                    <div className="quizAnswerMeta">
                      Your answer: <span className="picked">{r.options[r.selected_index]}</span>
                      {!r.correct && (
                        <>
                          {" "}
                          · Correct: <span className="correctOpt">{r.options[r.correct_index]}</span>
                        </>
                      )}
                    </div>
                    <div className="quizExplanation">{r.explanation}</div>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            questions.length > 0 && (
              <div className="quizTaking">
                {questions.map((q, idx) => (
                  <fieldset key={q.id} className="quizQuestionBlock">
                    <legend>
                      {idx + 1}. {q.question}
                    </legend>
                    {q.options.map((opt, optIdx) => (
                      <label key={optIdx} className="quizOption">
                        <input
                          type="radio"
                          name={`q-${q.id}`}
                          checked={selections[q.id] === optIdx}
                          disabled={busy}
                          onChange={() =>
                            setSelections((prev) => ({ ...prev, [q.id]: optIdx }))
                          }
                        />
                        <span>{opt}</span>
                      </label>
                    ))}
                  </fieldset>
                ))}
                <button type="button" disabled={busy || !allAnswered} onClick={submitQuiz}>
                  {busy ? "Scoring…" : "Submit answers"}
                </button>
              </div>
            )
          )}

          {history.length > 0 && (!questions.length || results) ? (
            <div className="quizHistory">
              <div className="cardHeader" style={{ marginTop: 16 }}>
                Recent scores (this file)
              </div>
              <ul>
                {history.slice(0, 8).map((h) => (
                  <li key={h.id}>
                    {h.score}/{h.max_score} ({h.percentage}%)
                    {h.submitted_at
                      ? ` · ${new Date(h.submitted_at).toLocaleString()}`
                      : null}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
