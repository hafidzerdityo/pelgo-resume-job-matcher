# CV Scoring & Job Matcher

An asynchronous system designed to score candidate resumes against job descriptions using Mistral AI, built with a robust worker-based architecture.

## 🚀 Getting Started

1.  **Environment Configuration**:  
    Navigate to the `be-cv-scoring/` directory and copy the example environment file:
    ```bash
    cp be-cv-scoring/.env.example be-cv-scoring/.env
    ```
2.  **Mistral AI Key**:  
    Open the newly created `.env` file and provide your `MISTRAL_API_KEY`. You can generate one at [console.mistral.ai](https://console.mistral.ai/).
3.  **Launch via Docker**:  
    From the root directory, run the full stack:
    ```bash
    docker-compose up --build -d
    ```
    or if you using newer docker compose version:
    ```bash
    docker compose up --build -d
    ```
    *All services are interconnected via Docker bridge network.*
4.  **Run Integration Tests**:  
    Verify the full system lifecycle (API -> Redis -> Worker -> DB) by running:
    ```bash
    docker exec pelgo-api pytest -s -v tests/integration/test_api_lifecycle.py
    ```

## 🏗️ Architectural Decisions

*   **Simple Layered Architecture**: Instead of over-engineering with something like "Clean Architecture," I opted for a focused **Layered Architecture (API -> Service -> Repository)**. This ensures clear separation of concerns without unnecessary abstraction overhead for this project scope.
*   **Out-of-Process Workers**: Utilized **Celery + Redis** over FastAPI's internal `BackgroundTask` to ensure heavy scraping and LLM tasks are **fully out-of-process**, preventing resource contention within the API process.
*   **Observability**: Implemented structured logging using **`structlog`** with a custom **`log_flow`** utility to maintain high observability across all layers (Handler, Service, Repository, and Worker).
*   **Reliability & DLQ**: Integrated a 3-retry limit for transient failures. Jobs that exceed this limit are transitioned to a "Dead" status, effectively simulating a Dead Letter Queue (DLQ) behavior for manual intervention.

## ✅ Testing & Validation

*   **API Lifecycle Integration**: A legit `pytest` suite in `be-cv-scoring/tests/integration/test_api_lifecycle.py` that hits the live API, uses seeded candidate data, and polls for asynchronous results.
*   **Frontend Polling**: Architectural test blueprint in `fe-cv-scoring/src/hooks/useMatches.test.ts` designed to verify the polling lifecycle (Start on 'processing' -> Stop on 'completed').
*   **Rate Limiting**: Redis-backed rate limiter protects the job submission endpoints (429 Too Many Requests).

## 🤖 AI Prompts Used (The Engineering Process)

The project was realized through a sequence of specific technical directives:
1.  *"Initialize the project using the quiz prompt (quiz.md) as the baseline for Big picture of the project"*
2.  *"Refactor the backend into a Layered Architecture with strict Python Type Hinting for improved maintainability. Also make sure to use sql alchemy for orm and alembic for migrations"*
3.  *"Implement a Celery + Redis worker system to move processing entirely out of the API process (fully out-of-process execution)."*
4.  *"Integrate `structlog` and a `log_flow` context manager to ensure every layer has structured, traceable logging."*
5.  *"Add a retry mechanism with a 3-retry limit. If it fails beyond that, implement a 'Dead' status logic that allows manual retries from the frontend."*
6.  *"Develop a Next.js frontend with paginated results and modals for detail views. Ensure the UI handles complex polling and status transitions (Pending -> Processing -> Done/Failed) gracefully."*
7.  *"Write integration tests using Pytest that hit the live API endpoints and poll for async worker results using the real database."*
8.  *"Finalize the Docker Compose setup to ensure all services communicate over a private bridge network with dynamic port mapping from `.env`."*

## 📝  Assumptions & Trade-offs

*   **Retry and Fault Handling**: The system is built for graceful degradation; if the Mistral AI provider is down, or URL scraping failed, jobs are safely moved to the `FAILED` state without impacting API availability or data integrity.
*   **Scraping Stability**: Scraping is assumed to be best-effort. The system prioritizes stability over exhaustive scraping, using a 10s timeout and a 8000-character context limit to prevent blowing up the LLM token budget.
*   **Security & Network Boundary**: This architecture assumes a **Trusted Internal Network** between service communication by simulating it through Docker Network Bridge.
*   **Polling vs. Push Architecture**: I deliberately chose **Short Polling** for the frontend over WebSockets. This trade-off prioritizes system simplicity for the MVP.
*   **Data Consistency**: We assume a "Write-Ahead" approach where the database is the source of truth for job status, while Redis acts strictly as a transport layer.
