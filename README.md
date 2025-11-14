[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DESIFpxz)
# CS_2025

## Description

Many educational institutions today face the problem of creating schedules for students. These schedules should have as few gaps as possible and be tailored to the wishes of teachers and school administrators. My project is a website where representatives of educational institutions can easily generate their own schedules. All you need to do is enter data about teachers, students, lessons, and classes at the educational institution, and then the algorithm will select the optimal schedule option, which you can download from the website in convenient formats and for different roles (groups, students, teachers, etc.). 
All information about the school is stored in encrypted form, so even the creators of the service cannot access personal data.

The platform consists of a React/Vite frontend, a FastAPI backend, PostgreSQL for relational data, and MinIO (S3 compatible) for secure file storage. Everything is containerized so the full stack can be launched with a single command during development or demo sessions.

## Setup

### 1. Bring up the full stack with Docker

Prerequisites:
- Docker (24+) and Docker Compose Plugin (v2)
- 4 GB RAM available for containers

```bash
docker compose up --build
```

The command starts the backend (FastAPI + uvicorn), the React frontend served by Nginx, PostgreSQL 18, and MinIO. Environment variables for the backend are already provided inside `docker-compose.yml`, but you can override them in a `.env` file at the repository root (Compose automatically picks it up).

### 2. Run services locally without Docker

**Backend**
```bash
cd backend
uv sync                  # install Python dependencies
cp .env.example .env               # populate using the variables in app/core/config.py
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Supporting infrastructure**
- PostgreSQL 15+ with a database/user that matches the variables in `.env`
- MinIO (recommended) or any S3-compatible storage; update `S3_ENDPOINT_URL`, credentials, and bucket name accordingly.

### 3. Helpful documentation
- `backend/README.md` contains backend-specific commands, migrations, and API notes.
- `frontend/README.md` explains Vite scripts, linting, and testing for the React app.

## Requirements

- **Backend**: Python 3.13, FastAPI, SQLAlchemy Async, Alembic, asyncpg, aioboto3.
- **Frontend**: React 19, TypeScript, Vite, Vitest, ESLint.
- **Infrastructure**: PostgreSQL 18 (or compatible), MinIO/S3, Docker & Compose for orchestration.
- **Tooling**: `uv` for Python dependency management, Node.js 20+ for the frontend toolchain.

## Features

- Generate conflict-free academic schedules tailored to students, groups, and teachers.
- Store institution data encrypted at rest; files live in MinIO/S3 and never on disk.
- Provide REST APIs for health checks and (soon) schedule management; backend wiring already includes database + storage lifecycles.
- Containerized stack for reproducible deployments and easy onboarding.
- Automated database migrations via Alembic during container startup.

## Git

The `main` branch stores the latest stable version deployed to demo environments. Create short-lived feature branches from `main` (e.g. `feature/schedules-api`) and open pull requests to keep history linear and reviewable.

## Success Criteria

- Users can create/update schedules.
- Generated timetables meet constraints (no teacher double-bookings, minimal gaps).
- API responses include downloadable artifacts for classrooms, groups, and teachers.
- Automated tests and health checks stay green across CI/CD and Docker runs.
