# FunDocs

FunDocs is a **document thinking partner**: sign in, unlock access with **Chapa**, upload **PDF / TXT / DOCX**, then **chat** with an AI that answers from your file, run **AI-generated quizzes** with scored results and explanations, and optionally turn on **Fun Mode** for playful, memorable explanations.

---

## What FunDocs is

FunDocs helps people **learn from their own documents** instead of drowning in pages of PDFs, notes, or policy files. You upload a file; the system **reads and indexes** the text, then answers questions **only using what is in that document** (retrieval-augmented generation). That makes it useful for **studying**, **exam prep**, **understanding contracts or reports**, and **onboarding** on internal material—without asking the model to invent facts from the open internet.

The app also **generates quizzes** from the same content so you can **check recall**, see a **score**, and read **short explanations** of the right answers. **Fun Mode** changes the tone of explanations (including optional cultural and **Amharic-flavored** phrasing in the AI instructions) so complex ideas can feel more approachable and memorable.

In short: **one place to upload, question, practice, and understand** the documents that matter to you.

---

## Why FunDocs fits Ethiopia

Ethiopia has a fast-growing **digital economy** and a large population of **students, teachers, civil servants, and entrepreneurs** who work with PDFs, Word files, and notes every day—often on mobile data and with limited time for tutoring or extra classes. FunDocs is designed around constraints and opportunities that are especially relevant there:

- **Payments with Chapa** — Checkout uses **[Chapa](https://developer.chapa.co/)**, an Ethiopian payment platform that supports **local methods** familiar to users (cards, mobile money, and other options Chapa exposes). That lowers friction compared with tools that assume only international cards or foreign billing.
- **Learning without a private tutor** — RAG chat and quizzes give learners a **24/7 study companion** grounded in *their* syllabus, handout, or regulation, which can help in **university prep**, **language and subject study**, and **professional certification** where one-on-one help is expensive or unavailable outside cities.
- **Trust in the source** — Answers are tied to **your uploaded file**, which matters when studying **official texts**, **workplace policies**, or **local curricula** where accuracy and traceability beat generic AI guesses.
- **Cultural and linguistic comfort** — **Fun Mode** is tuned so explanations can feel closer to how Ethiopians joke, tell stories, and mix **English with Amharic** in real conversation—useful for young people and anyone who retains information better when it feels **local and human**, not textbook-dry.
- **Digital inclusion** — A **web-based** stack (React + Django API) runs in the browser on common phones and laptops; no app-store gatekeeping is required to try the product once you host it.

FunDocs is not a replacement for teachers, lawyers, or doctors; it is a **productivity and learning layer** on top of documents Ethiopians already use, with **local payments** and **explanation styles** that match how many people actually study and work.

---

## Table of contents

- [What FunDocs is](#what-fundocs-is)
- [Why FunDocs fits Ethiopia](#why-fundocs-fits-ethiopia)
- [Features](#features)
- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [License](#license)

---

## Features

| Area | Description |
|------|-------------|
| **Authentication** | REST API with **JWT** (access token + refresh). Registration creates a user profile. |
| **Paywall** | **Chapa** payment; dashboard, uploads, chat, and quizzes require `has_access` on the user profile. |
| **Documents** | Upload PDF, plain text, or Word (`.docx`). Text is extracted, chunked, and indexed for retrieval. |
| **RAG chat** | Questions are grounded in **retrieved chunks** from the active document; answers use **Groq** chat completions. |
| **Quiz** | Generate multiple-choice questions from the document, submit answers, get a **score** and **per-question explanations** (Fun Mode affects explanation style). |
| **Fun Mode** | User preference stored server-side; adjusts system prompts for chat and quiz explanations. |

---

## Architecture

```text
┌─────────────┐     HTTPS / JSON      ┌──────────────────┐
│   React     │ ◄────────────────────► │  Django REST     │
│   (Vite)    │   JWT Bearer          │  + SimpleJWT     │
└─────────────┘                       └────────┬─────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    ▼                          ▼                          ▼
              SQLite (dev)                 Media / RAG                 Groq API
              User, docs,                chunks, TF-IDF or            chat + optional
              payments, quizzes          embeddings                   embeddings
```

- **Backend**: Django 5, Django REST Framework, `django-cors-headers`, **sqlite3** by default.
- **Retrieval**: Chunked document text + either **local TF-IDF** (default) or **Groq embeddings** (`EMBEDDINGS_BACKEND`).
- **Frontend**: React, React Router, Vite; API base URL from `VITE_API_BASE_URL`.

---

## Repository layout

| Path | Role |
|------|------|
| [`backend/`](backend/) | Django project: API, auth, Chapa, uploads, RAG, Groq, quiz logic. |
| [`frontend/`](frontend/) | React SPA: register/login flow, paywall, dashboard, upload, chat, quiz UI. |

---

## Prerequisites

- **Python** 3.10+ recommended  
- **Node.js** 18+ and npm  
- **Groq API key** ([Groq Console](https://console.groq.com/))  
- **Chapa** keys for payments (see [Chapa](https://developer.chapa.co/))  

---

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
# Edit .env — set DJANGO_SECRET_KEY, GROQ_API_KEY, CHAPA_* keys
python manage.py migrate
python manage.py runserver
```

API base: `http://127.0.0.1:8000/api/`

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if the API is not on localhost:8000
npm run dev
```

App URL (Vite default): `http://localhost:5173`

### 3. Smoke test

1. Register a user **with a real email** (required for Chapa checkout).  
2. Complete payment (or use **verify** flow after a test payment).  
3. Upload a document and wait until processing status is **done**.  
4. Chat or open **Quiz** on the dashboard.  

More detail: **[Backend README](backend/README.md)** · **[Frontend README](frontend/README.md)**

---

## Configuration

Secrets and environment-specific values live in **gitignored** files:

| File | Purpose |
|------|---------|
| `backend/.env` | Django, CORS, JWT, media path, Chapa, Groq, embeddings backend. |
| `frontend/.env` | `VITE_API_BASE_URL` pointing at the Django `/api` prefix. |

Templates: `backend/.env.example`, `frontend/.env.example`.

**Production checklist (high level)**

- Set `DJANGO_DEBUG=0`, restrict `DJANGO_ALLOWED_HOSTS`, set a strong `DJANGO_SECRET_KEY`.  
- Set `CORS_ALLOW_ORIGINS` to your real frontend origin(s).  
- Use a production database and static/media storage as appropriate.  
- Point `CHAPA_CALLBACK_URL` / `CHAPA_RETURN_URL` at public HTTPS URLs.  

---

## Documentation

- **[Backend API & setup](backend/README.md)** — endpoints, request/response shapes, environment variables.  
- **[Frontend setup & UI](frontend/README.md)** — dev server, env, feature overview.  

---

## License

Add a `LICENSE` file in this repository if you distribute the project; until then, rights are reserved by the project authors.
