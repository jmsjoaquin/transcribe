# transcribe-jmbj

Local-first transcription platform scaffold with:
- `FastAPI` backend
- `Redis` + `RQ` worker queue
- `PostgreSQL` for application data
- local media storage in development
- `faster-whisper` speech-to-text worker
- initial `Next.js` frontend scaffold

## Current Status

Working locally on macOS:
- user registration
- user login with cookie auth
- file upload
- async queue dispatch
- worker transcription processing
- transcript result fetch
- transcript download as `txt` and `json`
- logout
- delete transcription job

Not finished yet:
- production storage strategy beyond local/shared storage
- robust queue cancellation / job revocation
- frontend polish and full UX wiring
- full backend integration tests against a real PostgreSQL instance

## Repository Layout

```text
backend/
worker/
frontend/
```

## Local Runbook

### 1. Start dependencies

Make sure local PostgreSQL and Redis are running.

Example with Homebrew:

```bash
brew services start postgresql@14
brew services start redis
```

Check Redis:

```bash
redis-cli ping
```

Expected:

```text
PONG
```

### 2. Configure backend env

Create `backend/.env` with values similar to:

```env
APP_NAME=Transcribe API
DATABASE_URL=postgresql+psycopg://admin:password123@localhost:5433/transcribe_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-this-to-a-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ACCESS_TOKEN_COOKIE_NAME=access_token
ACCESS_TOKEN_COOKIE_SECURE=false
STORAGE_BACKEND=local
MEDIA_ROOT=./media
PUBLIC_MEDIA_BASE_URL=
CORS_ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

### 3. Run backend migrations and API

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Useful endpoints:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### 4. Run the worker on macOS

For macOS local smoke tests, use `SimpleWorker` mode to avoid the Objective-C `fork()` crash seen with default `rq.Worker`.

```bash
cd /Users/ali/Downloads/transcribe-jmbj
python3 -m venv worker/.venv
source worker/.venv/bin/activate
pip install -r worker/requirements.txt
export DATABASE_URL='postgresql+psycopg://admin:password123@localhost:5433/transcribe_db'
export REDIS_URL='redis://localhost:6379/0'
export STORAGE_BACKEND='local'
export MEDIA_ROOT='/Users/ali/Downloads/transcribe-jmbj/backend/media'
export WORKER_MEDIA_ACCESS_MODE='shared_storage'
export WORKER_USE_SIMPLE_WORKER='true'
export WHISPER_DEVICE='cpu'
export WHISPER_COMPUTE_TYPE='int8'
python -m worker.app.worker
```

Notes:
- `WORKER_USE_SIMPLE_WORKER=true` is for local macOS development only.
- On the Windows RTX worker, keep the normal worker mode and use CUDA settings.

### 5. Manual smoke test flow

Use Swagger at `http://127.0.0.1:8000/docs`.

Run these endpoints in order:
1. `POST /auth/register`
2. `POST /auth/login`
3. `POST /transcriptions/upload`
4. `GET /transcriptions/{job_id}`
5. `GET /transcriptions/{job_id}/result`
6. `GET /transcriptions/{job_id}/download?format=txt`
7. `GET /transcriptions/{job_id}/download?format=json`
8. `POST /auth/logout`
9. `DELETE /transcriptions/{job_id}`

## Automated Tests

Basic route smoke tests are under `backend/tests/`.

Run them with:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

These tests mock services and dependencies. They are meant to catch route wiring regressions quickly without requiring a live database or Redis instance.

## Frontend Scaffold

An initial Next.js app scaffold is available under `frontend/`.

To start it later:

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Default frontend URL:
- `http://127.0.0.1:3000`
