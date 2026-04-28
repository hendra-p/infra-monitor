from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from backend.core.config import settings
from backend.models.domain import Base, MetricRecord, InsightRecord
import json
import logging

logger = logging.getLogger("Storage")

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MetricStorage:
    def __init__(self, db_session):
        self.db = db_session

    def save_metric(self, payload):
        record = MetricRecord(
            timestamp=payload.timestamp,
            cpu_percent=payload.cpu_percent,
            memory_percent=payload.memory_percent,
            memory_used_gb=payload.memory_used_gb,
            memory_total_gb=payload.memory_total_gb,
            disk_percent=payload.disk_percent,
            disk_used_gb=payload.disk_used_gb,
            disk_total_gb=payload.disk_total_gb,
            top_processes_json=json.dumps([p.dict() for p in payload.top_processes])
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_metrics(self, limit: int = 100):
        return (
            self.db.query(MetricRecord)
            .order_by(MetricRecord.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_metrics_by_range(self, hours: int = 1):
        """Get metrics within a given time range (in hours). Max 14 days = 336 hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return (
            self.db.query(MetricRecord)
            .filter(MetricRecord.timestamp >= cutoff)
            .order_by(MetricRecord.timestamp.asc())
            .all()
        )

    def save_insight(self, insight):
        record = InsightRecord(
            timestamp=insight.timestamp,
            severity=insight.severity,
            component=insight.component,
            message=insight.message,
            root_cause=insight.root_cause
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_insights(self, limit: int = 20):
        return (
            self.db.query(InsightRecord)
            .order_by(InsightRecord.timestamp.desc())
            .limit(limit)
            .all()
        )

    def cleanup_old_data(self, retention_days: int = 14):
        """Delete data older than retention period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        deleted_metrics = self.db.query(MetricRecord).filter(MetricRecord.timestamp < cutoff).delete()
        deleted_insights = self.db.query(InsightRecord).filter(InsightRecord.timestamp < cutoff).delete()
        self.db.commit()
        if deleted_metrics or deleted_insights:
            logger.info(f"Cleaned up {deleted_metrics} metrics and {deleted_insights} insights older than {retention_days} days.")
