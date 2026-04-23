import psutil
from agent.core.base import MetricCollector
from agent.models.metrics import SystemMetricsPayload

class MemoryCollector(MetricCollector):
    def collect(self, payload: SystemMetricsPayload) -> None:
        mem = psutil.virtual_memory()
        payload.memory_percent = mem.percent
        payload.memory_used_gb = round(mem.used / (1024 ** 3), 2)
        payload.memory_total_gb = round(mem.total / (1024 ** 3), 2)
