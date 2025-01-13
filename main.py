# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
from typing import List
from database import SessionLocal, Base, engine
from models import ScheduledJob
from schemas import JobCreate, JobRead
from loguru import logger
import os


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/scheduler/jobs", response_model=List[JobRead])
def list_jobs(db: Session = Depends(get_db)):
    logger.info("Getting all jobs.")
    jobs = db.query(ScheduledJob).filter(ScheduledJob.status != "deleted").all()
    logger.success(f"Responded with the jobs.")
    return jobs

@app.post("/scheduler/jobs", response_model=JobRead)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    logger.info("Calculating next run")
    # Calculate the next_run_time based on the current date + run_time
    initial_next_run = calculate_next_run_time_for_creation(job_data.frequency, job_data.run_time)

    logger.info("Creating the job")
    job = ScheduledJob(
        frequency=job_data.frequency,
        run_time=job_data.run_time,
        number_of_days=job_data.number_of_days,
        list_of_companies=job_data.list_of_companies,
        next_run_time=initial_next_run
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.success("Job created and written on db")
    return job

@app.delete("/scheduler/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ScheduledJob).filter(ScheduledJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Hard delete or soft delete:
    # Hard delete:
    db.delete(job)
    # Or soft delete:
    # job.status = "deleted"
    
    db.commit()
    return {"detail": "Job deleted"}


def calculate_next_run_time_for_creation(frequency: str, run_time: time) -> datetime:
    """
    Example: 
    1) If current time is 14:30, and run_time is 00:00, 
       we might want to schedule it for "today at midnight" if it's not passed,
       or "tomorrow at midnight" if it already passed. 
    2) Then, next runs happen daily, weekly, or bi-weekly from there.
    """
    today = datetime.utcnow().date()
    # Combine 'today' with the desired run_time
    run_dt = datetime.combine(today, run_time)

    if run_dt <= datetime.utcnow():
        # If we've already passed that time today, schedule for tomorrow 
        # (or the next relevant day if frequency = weekly, etc.)
        if frequency == "daily":
            return run_dt + timedelta(days=1)
        elif frequency == "weekly":
            return run_dt + timedelta(days=7)
        elif frequency == "bi-weekly":
            return run_dt + timedelta(days=14)
        else:
            # default daily
            return run_dt + timedelta(days=1)
    else:
        # If we haven't yet reached today's run_time, use it.
        return run_dt


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if Railway doesn't provide a PORT variable
    uvicorn.run(app, host="0.0.0.0", port=port)
    
