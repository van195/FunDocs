# FunDocs — Frontend

Single-page app built with **React**, **Vite**, and **React Router**. It talks to the Django API using **JWT** storage in `localStorage` and a small `apiFetch` helper.

---

## Table of contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Scripts](#scripts)
- [Configuration](#configuration)
- [Features & flows](#features--flows)
- [Project structure](#project-structure)

---

## Requirements

- **Node.js** 18+ (20 LTS recommended)
- npm (ships with Node)

---

## Setup

```bash
cd frontend
npm install
cp .env.example .env    # Windows: copy .env.example .env
```

Edit `.env` if the API is not at the default:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

Start the dev server:

```bash
npm run dev
```

Default URL: **http://localhost:5173**

Ensure the backend is running and CORS allows this origin (see `backend/.env` → `CORS_ALLOW_ORIGINS`).

---

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Vite dev server with HMR. |
| `npm run build` | Production build to `dist/`. |
| `npm run preview` | Serve the production build locally. |

---

## Configuration

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Base URL for API calls **including** the `/api` path prefix (e.g. `http://localhost:8000/api`). |

Vite only exposes variables prefixed with `VITE_`.

---

## Features & flows

1. **Landing / navigation** — Home and registration entry points (see `App.jsx` and routing).  
2. **Register / login** — Obtains JWT access token; stored via `src/api.js`.  
3. **Paywall** — If `me.has_access` is false, the UI prompts for Chapa payment and optional “verify” after returning from checkout.  
4. **Dashboard** — Upload documents, pick an active file, **chat** with RAG, toggle **Fun Mode** (persisted with `PATCH /me/preferences/`).  
5. **Quiz** — For a fully processed document, generate MCQs, answer, submit for score and AI explanations (style follows server-side `fun_mode` at submit time).  

---

## Project structure

| Path | Role |
|------|------|
| `src/main.jsx` | App bootstrap, global styles, router shell. |
| `src/App.jsx` | Auth state, paywall, dashboard gate, shared components (`ChatBox`, `FunModeToggle`, etc.). |
| `src/api.js` | `API_BASE_URL`, token helpers, `apiFetch`. |
| `src/pages/` | Page-level views (`home`, `register`, `dashboard`). |
| `src/pages/dashbord/QuizSection.jsx` | Quiz UI (generate, answer, results, history). |
| `src/styles.css` | Global layout, dashboard, chat, quiz styles. |

> Note: some folder names use existing spelling (e.g. `dashbord`) to match the codebase.

---

## Related docs

- [Project overview & quick start](../README.md)  
- [Backend API & environment](../backend/README.md)  
