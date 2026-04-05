import httpx
import time
import os
import pytest

# Configuration from environment or defaults
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

def test_full_batch_lifecycle_via_api():
    """
    Legit Integration Test (Black-Box style).
    Submits multiple scenarios in a SINGLE BATCH to avoid rate limiting 
    and verify the batch processing capability.
    """
    with httpx.Client(timeout=30.0) as client:
        # 1. Fetch candidate from seed
        res = client.get(f"{API_URL}/candidates")
        assert res.status_code == 200
        candidates = res.json()
        assert len(candidates) > 0
        candidate_id = candidates[0]["id"]

        # 2. Define Scenarios
        scenarios = [
            {"name": "VALID_KALIBRR", "payload": {"url": "https://www.kalibrr.id/id-ID/c/leapfroggr-inc/jobs/65701/back-end-developer"}, "expected": ["completed", "failed"]},
            {"name": "FAILED_WWR", "payload": {"url": "https://weworkremotely.com/remote-jobs/close-senior-software-engineer-backend-python-usa-only-100-remote-1"}, "expected": ["failed", "dead"]},
            {"name": "RAW_TEXT", "payload": {"text": "Requirements: Python, FastAPI, SQL."}, "expected": ["completed"]}
        ]

        # 3. Submit ALL jobs in one Batch (Single POST request to avoid 429)
        print(f"\n📤 Submitting batch of {len(scenarios)} jobs...")
        res = client.post(f"{API_URL}/matches", json={
            "candidate_id": candidate_id,
            "jobs": [s["payload"] for s in scenarios]
        })
        assert res.status_code == 201, f"Batch submission failed: {res.text}"
        
        submitted_jobs = res.json()["jobs"]
        assert len(submitted_jobs) == len(scenarios)
        
        # Map job_ids to their scenario expectations
        job_tracking = []
        for i, job in enumerate(submitted_jobs):
            job_tracking.append({
                "id": job["id"],
                "expected": scenarios[i]["expected"],
                "name": scenarios[i]["name"]
            })

        # 4. Polling for all results
        print("⏳ Polling for worker results...")
        completed_count = 0
        timeout = 60
        start_time = time.time()
        final_results = {}

        while len(final_results) < len(job_tracking) and (time.time() - start_time) < timeout:
            for item in job_tracking:
                jid = item["id"]
                if jid in final_results: continue
                
                r = client.get(f"{API_URL}/matches/{jid}")
                data = r.json()
                if data["status"] in ["completed", "failed", "dead"]:
                    final_results[jid] = data
                    print(f"🏁 Job {item['name']} finished as {data['status']}")
            
            if len(final_results) < len(job_tracking):
                time.sleep(2)

        # 5. Final Assertions & Pretty Reporting
        print("\n" + "="*60)
        print(f"{'SCENARIO NAME':<20} | {'EXPECTED':<15} | {'RESULT':<10} | {'STATUS'}")
        print("-" * 60)
        
        all_passed = True
        for item in job_tracking:
            result = final_results[item["id"]]
            status_icon = "✅" if result["status"] in item["expected"] else "❌"
            
            print(f"{item['name']:<20} | {str(item['expected']):<15} | {result['status']:<10} | {status_icon}")
            
            if result["status"] not in item["expected"]:
                all_passed = False
            
            if result["status"] == "completed":
                # Print a bit of the AI recommendation for legit feel
                rec_preview = result["recommendation"][:50] + "..."
                print(f"   └─ Score: {result['overall_score']}% | AI: {rec_preview}")

        print("="*60)
        assert all_passed, "One or more scenarios failed their status expectation!"
