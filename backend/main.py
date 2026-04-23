from fastapi import FastAPI, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
import logging

from backend.core.config import settings
from backend.schemas.api_models import SystemMetricsPayload, SystemInsight
from backend.services.storage import get_db, init_db, MetricStorage
from backend.services.analysis import AnalysisEngine
from backend.services.alerting import AlertManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("API")

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    logger.info(f"{settings.PROJECT_NAME} started. Connected to PostgreSQL.")

# Singletons
analysis_engine = AnalysisEngine()
alert_manager = AlertManager()


def _process_and_alert(payload: SystemMetricsPayload, db: Session):
    """Background task: analyze metrics and trigger alerts."""
    storage = MetricStorage(db)
    insights = analysis_engine.analyze(payload)
    for insight in insights:
        storage.save_insight(insight)
    if insights:
        alert_manager.process_insights(insights)
    # Periodic cleanup (runs on every ingest, but cleanup is cheap)
    storage.cleanup_old_data(settings.RETENTION_DAYS)


@app.post(f"{settings.API_V1_STR}/metrics", response_model=dict)
def ingest_metrics(
    payload: SystemMetricsPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    storage = MetricStorage(db)
    storage.save_metric(payload)
    background_tasks.add_task(_process_and_alert, payload, db)
    return {"status": "success", "message": "Metrics ingested"}


@app.get(f"{settings.API_V1_STR}/metrics", response_model=List[SystemMetricsPayload])
def get_metrics(
    limit: int = Query(50, ge=1, le=5000, description="Max records to return"),
    hours: int = Query(None, ge=1, le=336, description="Filter metrics by last N hours (max 336 = 14 days)"),
    db: Session = Depends(get_db)
):
    storage = MetricStorage(db)

    if hours:
        records = storage.get_metrics_by_range(hours)
    else:
        records = storage.get_latest_metrics(limit)

    result = []
    for r in records:
        result.append(SystemMetricsPayload(
            timestamp=r.timestamp,
            cpu_percent=r.cpu_percent,
            memory_percent=r.memory_percent,
            memory_used_gb=r.memory_used_gb,
            memory_total_gb=r.memory_total_gb,
            disk_percent=r.disk_percent,
            disk_used_gb=r.disk_used_gb,
            disk_total_gb=r.disk_total_gb,
            top_processes=json.loads(r.top_processes_json) if r.top_processes_json else []
        ))

    # If fetched by latest (desc), reverse for chronological order
    if not hours:
        result.reverse()

    return result


@app.get(f"{settings.API_V1_STR}/insights", response_model=List[SystemInsight])
def get_insights(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    storage = MetricStorage(db)
    records = storage.get_latest_insights(limit)
    return [
        SystemInsight(
            timestamp=r.timestamp,
            severity=r.severity,
            component=r.component,
            message=r.message,
            root_cause=r.root_cause
        ) for r in records
    ]
