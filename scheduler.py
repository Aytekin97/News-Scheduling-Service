import time
import requests
from datetime import datetime, timedelta
from database import SessionLocal
from models import ScheduledJob
from config import settings


AGGREGATOR_API_URL = settings.aggregator_api_url

def run_scheduled_jobs():
    """
    Periodically checks the DB for jobs that are due to run, 
    calls the News-Aggregator API, and updates next_run_time.
    """
    while True:
        now = datetime.utcnow()
        db = SessionLocal()

        # Fetch all active jobs due to run now or in the past
        jobs = db.query(ScheduledJob).filter(
            ScheduledJob.status == "active",
            ScheduledJob.next_run_time <= now
        ).all()

        for job in jobs:
            # Call News-Aggregator with required parameters
            payload = {
                "companies": job.list_of_companies,
                "number_of_days": job.number_of_days
            }
            try:
                response = requests.post(AGGREGATOR_API_URL, json=payload)
                response.raise_for_status()
                print(f"Job {job.id} executed successfully.")
                
                # If repeat == true, schedule next_run_time
                if job.repeat:
                    job.next_run_time = calculate_next_run_time(job.frequency)
                else:
                    # Mark job as completed or inactive
                    job.status = "completed"

                db.commit()
            
            except Exception as e:
                print(f"Error running job {job.id}: {e}")
                # Optionally add retry logic, or mark job as "failed"

        db.close()
        # Sleep for 60 seconds, adjust as needed
        time.sleep(60)

def calculate_next_run_time(frequency: str):
    """
    Very simplistic: if 'daily', add 24h; if 'hourly', add 1h, etc.
    Or parse a cron string, etc.
    """
    now = datetime.utcnow()
    if frequency == "daily":
        return now + timedelta(days=1)
    elif frequency == "hourly":
        return now + timedelta(hours=1)
    else:
        # default: let's say every 24h
        return now + timedelta(days=1)


if __name__ == "__main__":
    run_scheduled_jobs()