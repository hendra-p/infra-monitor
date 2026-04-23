import psutil
from agent.core.base import MetricCollector
from agent.models.metrics import SystemMetricsPayload, ProcessInfo

class ProcessCollector(MetricCollector):
    def collect(self, payload: SystemMetricsPayload) -> None:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                # Only care about processes using actual resources to keep payload small
                if pinfo.get('cpu_percent', 0) > 1.0 or pinfo.get('memory_percent', 0) > 1.0:
                    processes.append(
                        ProcessInfo(
                            pid=pinfo['pid'],
                            name=pinfo['name'],
                            cpu_percent=round(pinfo['cpu_percent'] or 0.0, 2),
                            memory_percent=round(pinfo['memory_percent'] or 0.0, 2)
                        )
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU usage and get top 5
        processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        payload.top_processes = processes[:5]
