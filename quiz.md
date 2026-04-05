# Senior Full-Stack Assignment (4–6 hours)

AI tools are explicitly encouraged. Use GitHub Copilot, Cursor, ChatGPT, Claude, whatever helps you move fast. We will ask you to share your prompts and explain every decision.

---

## Background

Pelgo is a career-transition platform. Candidates upload a resume, the system finds matching jobs and scores each one (0–100%) against the candidate's skills and experience. A coaching layer explains the gaps and generates a personalised learning path.

You are joining the core product team. This assignment is a small, realistic slice of work you would encounter in your first few weeks.

---

## The Task — Async Match Pipeline

Build a system where a client submits one or more job descriptions for scoring against a candidate profile, the scoring runs as a background job, and the client can poll for results or receive them via a simple status endpoint.

---

## Backend — Python / FastAPI

### API Endpoints

#### POST /api/v1/matches
- Accept a batch of up to 10 job descriptions (plain text or URLs)
- Enqueue a background scoring job for each
- Return immediately with a list of job IDs and status `pending`

#### GET /api/v1/matches/{id}
- Return the current status and result for a single match job
- Status must be one of:
  - `pending`
  - `processing`
  - `completed`
  - `failed`

#### GET /api/v1/matches?status=&limit=&offset=
- List match results for the current candidate
- Filterable by status
- Must support pagination

---

## Scoring Worker

- Runs out-of-process as a background worker (not inside API process)
- For each job:
  - Extract required skills and seniority from the description
  - Compare against candidate profile in PostgreSQL
  - Compute:
    - Overall score (0–100)
    - Per-dimension scores (skills, experience, location)
- Handle failures gracefully (one bad job must not crash others)
- At least 2 workers must run concurrently without duplicate/corrupt results
- Can use LLMs or custom logic

---

## Data Model — PostgreSQL

- Design and implement schema
- Include migrations (Alembic or plain SQL)
- Candidate profile must be stored in DB (not hardcoded)
- Include seed script

---

## Frontend — React / Next.js

- Form to submit 1–10 job descriptions (URL or text)
- Results list polling `GET /api/v1/matches` (real-time updates, no reload)
- Each result shows:
  - Overall match %
  - Per-dimension scores
  - Matched skills
  - Missing skills
  - Recommendation string
- UI states must be distinct:
  - `pending`
  - `processing`
  - `completed`
  - `failed`

---

## Requirements

### Must Have

- POST, GET by ID, and GET list endpoints working
- True async out-of-process worker
- At least 2 workers without race conditions
- PostgreSQL schema + migrations + seed
- Frontend polling + clear UI states
- At least 1 backend integration test (full lifecycle)
- At least 1 frontend test (polling + state transitions)
- README including:
  - Setup
  - Architectural decisions
  - How to run workers
  - Assumptions
  - AI prompts used
- Deployed system (API + frontend live)

---

### Should Have

- `docker-compose.yml` (API + worker + Postgres + queue)
- Structured logging (job ID, status transitions, timing)
- Input validation with meaningful error messages
- Environment-based config (no hardcoded secrets)
- Type hints in Python

---

### Nice to Have

- URL scraping when job URL is submitted
- Dead-letter queue for failed jobs
- Admin endpoint to re-queue failed jobs
- Rate limiting on POST endpoint

---

## On Time Management

This is scoped for 4–6 hours intentionally. If you cannot complete everything, prioritize a working core and document trade-offs. A working core with README notes is better than a half-finished feature.

---

## Submission

1. Push to a public GitHub repository
2. Deploy full stack (API + worker + frontend live)

Email:
- devesh@pelgo.com
- wu@pelgo.com

Subject:
**Pelgo Assignment — [Your Name]**

Deadline: **3 days from receipt**

Be honest about how much actual time you spent completing the assignment.

---

## Evaluation Criteria

| Dimension | Points | What Great Looks Like |
|----------|--------|----------------------|
| Architecture | 25 pts | Out-of-process worker, correct job claiming, isolated failures |
| Data model & migrations | 20 pts | Clean schema, working migrations, seed script |
| API design | 15 pts | Proper status codes, pagination, consistent errors |
| Code quality | 15 pts | Readable, typed, not over-engineered |
| Testing | 15 pts | Integration + frontend tests that actually test behavior |
| README & decisions | 10 pts | Easy setup, documented trade-offs and AI prompts |