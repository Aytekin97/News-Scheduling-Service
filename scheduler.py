import time
import requests
from datetime import datetime, timedelta, date
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

                # After a run, schedule the next run based on frequency + time_of_day
                job.next_run_time = calculate_next_run_time(job.frequency, job.run_time)
                db.commit()
            
            except Exception as e:
                print(f"Error running job {job.id}: {e}")
                # Optionally add retry logic, or mark job as "failed"

        db.close()
        time.sleep(60)

def calculate_next_run_time(frequency: str, run_time) -> datetime:
    """
    For daily, add 1 day, for weekly add 7 days, for bi-weekly add 14 days,
    then combine with run_time (which is a time object) for the next date.

    Example:
      if frequency == "daily", next run = (today + 1 day) at run_time.
    """
    now = datetime.utcnow()
    today = now.date()

    if frequency == "daily":
        delta_days = 1
    elif frequency == "weekly":
        delta_days = 7
    elif frequency == "bi-weekly":
        delta_days = 14
    else:
        # default daily
        delta_days = 1

    # The next run date is today + delta_days
    next_run_date = today + timedelta(days=delta_days)
    return datetime.combine(next_run_date, run_time)


if __name__ == "__main__":
    run_scheduled_jobs()