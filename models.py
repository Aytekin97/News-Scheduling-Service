from sqlalchemy import Column, Integer, String, Boolean, DateTime, text, Time
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from database import Base


class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id = Column(Integer, primary_key=True, index=True)

    # "daily", "weekly", or "bi-weekly"
    frequency = Column(String, nullable=False)

    # E.g., "00:00" for midnight, or store as a Time column
    run_time = Column(Time, nullable=False)

    # For how many days in the past the aggregator should go
    number_of_days = Column(Integer, nullable=False, default=1)

    # Postgres array of company names
    list_of_companies = Column(ARRAY(String), nullable=False, server_default="{}")

    status = Column(String, default="active")  # "active", "completed", etc.
    next_run_time = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"),
                        onupdate=text("CURRENT_TIMESTAMP"))
    