from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timezone

class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float

class SystemMetricsPayload(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    top_processes: List[ProcessInfo] = []

class InsightSeverity(BaseModel):
    level: str  # "INFO", "WARNING", "CRITICAL"

class SystemInsight(BaseModel):
    timestamp: datetime
    severity: str
    component: str # "CPU", "Memory", "Disk"
    message: str
    root_cause: Optional[str] = None
