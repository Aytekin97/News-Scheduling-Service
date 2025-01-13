from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from database import Base

class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id = Column(Integer, primary_key=True, index=True)
    frequency = Column(String, nullable=False)
    repeat = Column(Boolean, default=True)
    number_of_days = Column(Integer, nullable=False, default=1)
    list_of_companies = Column(ARRAY(String), nullable=False, server_default="{}")
    status = Column(String, default="active")
    next_run_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"),
                        onupdate=text("CURRENT_TIMESTAMP"))
