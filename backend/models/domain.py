import json
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class MetricRecord(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    memory_used_gb = Column(Float)
    memory_total_gb = Column(Float)
    disk_percent = Column(Float)
    disk_used_gb = Column(Float)
    disk_total_gb = Column(Float)
    top_processes_json = Column(Text)

    # Composite index for efficient time-range queries
    __table_args__ = (
        Index('idx_metrics_timestamp_cpu', 'timestamp', 'cpu_percent'),
    )

class InsightRecord(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String(20), index=True)
    component = Column(String(50))
    message = Column(String(500))
    root_cause = Column(String(500), nullable=True)
