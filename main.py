# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from database import SessionLocal, Base, engine
from models import ScheduledJob
from schemas import JobCreate, JobRead
import os


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
    jobs = db.query(ScheduledJob).filter(ScheduledJob.status != "deleted").all()
    return jobs

@app.post("/scheduler/jobs", response_model=JobRead)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    job = ScheduledJob(
        frequency=job_data.frequency,
        repeat=job_data.repeat,
        number_of_days=job_data.number_of_days,
        list_of_companies=job_data.list_of_companies,
        next_run_time=datetime.utcnow()  # or calculate next run
    )
    db.add(job)
    db.commit()
    db.refresh(job)
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


if __name__ == "__main__":
    import uvicorn
    Base.metadata.create_all(bind=engine)
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if Railway doesn't provide a PORT variable
    uvicorn.run(app, host="0.0.0.0", port=port)
    
