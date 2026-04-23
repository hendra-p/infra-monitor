from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float

class SystemMetricsPayload(BaseModel):
    timestamp: str # Using str for easier JSON serialization from agent
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    top_processes: List[ProcessInfo] = []
