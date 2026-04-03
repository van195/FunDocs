## FunDocs Django + React Project

This is a friendly “thinking partner” app:

- Django REST API (JWT auth)
- Chapa payment paywall (user cannot access dashboard until paid)
- Upload `pdf/txt/docx` files
- Groq-powered RAG chat over the uploaded file
- “Fun Mode” toggle that changes the explanation style (fun, easy-to-remember, like explaining to a child)

### Repo structure

- `backend/` Django project (API, auth, payments, file upload, Groq/RAG)
- `frontend/` React app (login/register, paywall, upload, chat UI)

### Important: secrets



- `backend/.env`
- `frontend/.env` 



