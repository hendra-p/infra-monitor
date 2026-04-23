import psutil
from agent.core.base import MetricCollector
from agent.models.metrics import SystemMetricsPayload

class DiskCollector(MetricCollector):
    def collect(self, payload: SystemMetricsPayload) -> None:
        try:
            disk = psutil.disk_usage('/')
            payload.disk_percent = disk.percent
            payload.disk_used_gb = round(disk.used / (1024 ** 3), 2)
            payload.disk_total_gb = round(disk.total / (1024 ** 3), 2)
        except Exception:
            # On some systems, '/' might not be the right path or accessible
            pass
