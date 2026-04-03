## Backend (Django REST)

### Setup
1. `cd backend`
2. `copy .env.example .env` and fill keys.
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py runserver`

### API Endpoints
- `POST /api/auth/register/`
- `POST /api/auth/login/` (JWT access token returned)
- `GET /api/me/`
- `PATCH /api/me/preferences/` (currently only `fun_mode`)
- `POST /api/payments/chapa/create/` (returns `authorization_url`)
- `POST /api/payments/chapa/callback/` (Chapa webhook)
- `POST /api/documents/upload/` (multipart file)
- `GET /api/documents/`
- `POST /api/chat/ask/`

