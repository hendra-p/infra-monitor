import psutil
from agent.core.base import MetricCollector
from agent.models.metrics import SystemMetricsPayload

class CpuCollector(MetricCollector):
    def collect(self, payload: SystemMetricsPayload) -> None:
        # Using interval=None for non-blocking call. Returns value since last call.
        payload.cpu_percent = psutil.cpu_percent(interval=None)
