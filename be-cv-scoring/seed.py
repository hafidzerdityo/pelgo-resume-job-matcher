"""Seed script to populate the database with sample candidate profiles.

Usage:
    docker compose exec pelgo-api python seed.py
    - or locally -
    python seed.py
"""
from app.database import SessionLocal
from app.models.candidate import CandidateProfile
from app.models.match import MatchJob  # noqa: F401 — ensure table exists


def seed() -> None:
    """Insert sample candidate profiles if they don't already exist."""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing = db.query(CandidateProfile).first()
        if existing is not None:
            print("Database already seeded. Skipping.")
            return

        candidates: list[CandidateProfile] = [
            CandidateProfile(
                name="Alice Johnson",
                email="alice@example.com",
                skills=[
                    "Python", "FastAPI", "Django", "PostgreSQL", "Docker",
                    "AWS", "REST API", "SQLAlchemy", "Git", "CI/CD",
                ],
                experience_years=5,
                location="San Francisco, CA",
                seniority="senior",
                resume_text=(
                    "Senior software engineer with 5 years of experience in backend development. "
                    "Proficient in Python, FastAPI, Django, and cloud infrastructure. "
                    "Led migration of monolith to microservices architecture at previous company. "
                    "Strong experience with PostgreSQL, Docker, and AWS services."
                ),
            ),
            CandidateProfile(
                name="Bob Smith",
                email="bob@example.com",
                skills=[
                    "JavaScript", "TypeScript", "React", "Next.js", "Node.js",
                    "CSS", "HTML", "GraphQL", "MongoDB", "Git",
                ],
                experience_years=3,
                location="New York, NY",
                seniority="mid",
                resume_text=(
                    "Full-stack developer with 3 years of experience specialising in React "
                    "and Next.js applications. Built and maintained e-commerce platforms "
                    "serving 100K+ users. Comfortable with both frontend and backend work "
                    "using Node.js and GraphQL."
                ),
            ),
            CandidateProfile(
                name="Carol Davis",
                email="carol@example.com",
                skills=[
                    "Python", "Machine Learning", "TensorFlow", "PyTorch",
                    "SQL", "Pandas", "NumPy", "Docker", "Kubernetes", "Spark",
                ],
                experience_years=7,
                location="London, UK",
                seniority="lead",
                resume_text=(
                    "ML Engineering Lead with 7 years of experience building production ML systems. "
                    "Designed and deployed recommendation engines, NLP pipelines, and real-time "
                    "inference systems. Led a team of 4 engineers. Expert in Python, TensorFlow, "
                    "and distributed computing with Spark."
                ),
            ),
        ]

        db.add_all(candidates)
        db.commit()
        print(f"Seeded {len(candidates)} candidate profiles.")

        for c in candidates:
            db.refresh(c)
            print(f"  - {c.name} (ID: {c.id})")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
