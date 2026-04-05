import time

from celery import Celery
import structlog
import json
import httpx
from bs4 import BeautifulSoup
from mistralai import Mistral

from app.config import settings
from app.database import SessionLocal
from app.models.match import MatchJob, MatchStatus
from app.models.candidate import CandidateProfile
from app.logger import setup_logging, get_logger

setup_logging()
logger = get_logger("celery_worker")

celery_app = Celery(
    "pelgo_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

def scrape_job_description(url: str) -> str:
    """Fetch and extract text from a job URL."""
    try:
        logger.info("scraping_url", url=url)
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean up whitespace
            text = soup.get_text(separator=" ")
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            
            # Limit length to avoid blowing up LLM context if it's too huge
            return text[:8000]
    except Exception as e:
        logger.error("scraping_failed", url=url, error=str(e))
        raise ValueError(f"Failed to scrape job description from {url}: {str(e)}")


def calculate_score_llm(candidate: CandidateProfile, job_desc: str) -> dict:
    """Use Mistral LLM to score the job match."""
    client = Mistral(api_key=settings.MISTRAL_API_KEY)
    
    prompt = f"""
    You are an expert HR recruiter. Your task is to score a candidate against a job description.
    
    Candidate Profile:
    - Name: {candidate.name}
    - Skills: {', '.join(candidate.skills)}
    - Experience: {candidate.experience_years} years
    - Seniority: {candidate.seniority}
    - Location: {candidate.location}
    - Resume Text: {candidate.resume_text}
    
    Job Description:
    {job_desc}
    
    Please evaluate the match and provide the following in JSON format:
    {{
        "overall_score": (0-100),
        "skill_score": (0-100),
        "experience_score": (0-100),
        "location_score": (0-100),
        "matched_skills": ["list", "of", "matched", "skills"],
        "missing_skills": ["list", "of", "missing", "skills"],
        "recommendation": "A brief explanation of why this candidate is or isn't a good fit."
    }}
    
    ONLY return the JSON object.
    """

    try:
        chat_response = client.chat.complete(
            model="mistral-medium-latest",
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"}
        )
        resp_text = chat_response.choices[0].message.content
        return json.loads(resp_text)
    except Exception as e:
        logger.error("llm_scoring_failed", error=str(e))
        raise e


@celery_app.task(name="score_match_job", bind=True, max_retries=3)
def score_match_job(self, job_id_str: str) -> str:
    start_time = time.time()
    
    # Bind structlog context variables for the entire task
    structlog.contextvars.bind_contextvars(job_id=job_id_str)
    
    logger.info("job_started", message="Started processing match job")
    
    db = SessionLocal()
    try:
        from uuid import UUID
        job_id = UUID(job_id_str)
        
        job = db.query(MatchJob).filter(MatchJob.id == job_id).first()
        if not job:
            logger.error("job_not_found", message=f"Job not found in database.")
            return "not_found"
            
        # Transition to PROCESSING
        old_status = job.status
        job.status = MatchStatus.PROCESSING.value
        db.commit()
        logger.info("status_transition", old_status=old_status, new_status=job.status)
        
        # Simulate processing time (e.g. LLM API call time)
        time.sleep(1.5)
        
        candidate = db.query(CandidateProfile).filter(CandidateProfile.id == job.candidate_id).first()
        if not candidate:
             raise ValueError(f"Candidate {job.candidate_id} not found.")
             
        # Scrape job description if it's a URL
        if job.source_url:
            job_desc = scrape_job_description(job.source_url)
        else:
            job_desc = job.job_description
             
        # Always use LLM scoring
        logger.info("using_llm_scoring", job_id=job_id_str)
        scores = calculate_score_llm(candidate, job_desc)
        
        # Update Job
        job.overall_score = scores["overall_score"]
        job.skill_score = scores["skill_score"]
        job.experience_score = scores["experience_score"]
        job.location_score = scores["location_score"]
        job.matched_skills = scores["matched_skills"]
        job.missing_skills = scores["missing_skills"]
        job.recommendation = scores["recommendation"]
        
        old_status = job.status
        job.status = MatchStatus.COMPLETED.value
        db.commit()
        
        elapsed = time.time() - start_time
        logger.info("status_transition", old_status=old_status, new_status=job.status)
        logger.info("job_completed", status="completed", elapsed_seconds=round(elapsed, 2))
        return "completed"
        
    except Exception as e:
        db.rollback()
        logger.exception("job_failed", error=str(e))
        
        # transition to failed or dead
        try:
            from uuid import UUID
            job = db.query(MatchJob).filter(MatchJob.id == UUID(job_id_str)).first()
            if job:
                job.retry_count = self.request.retries + 1
                if self.request.retries >= self.max_retries:
                    job.status = MatchStatus.DEAD.value
                    logger.warning("job_marked_dead", job_id=job_id_str, retries=job.retry_count)
                else:
                    job.status = MatchStatus.FAILED.value
                
                job.error_message = str(e)
                db.commit()
                logger.info("status_transition", old_status="PROCESSING", new_status=job.status)
        except Exception as inner_e:
            logger.exception("status_transition_failed", message="Could not update job status in DB", inner_error=str(inner_e))
            
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=10)
        else:
            return "failed_dead"
    finally:
        db.close()
        structlog.contextvars.clear_contextvars()
