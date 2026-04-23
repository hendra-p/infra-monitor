from typing import List, Optional
from datetime import datetime
from backend.schemas.api_models import SystemMetricsPayload, SystemInsight
from backend.core.config import settings

class RuleEngine:
    def evaluate(self, metrics: SystemMetricsPayload) -> List[SystemInsight]:
        insights = []
        
        # CPU Rules
        if metrics.cpu_percent >= settings.CPU_CRITICAL_THRESHOLD:
            insights.append(SystemInsight(
                timestamp=metrics.timestamp,
                severity="CRITICAL",
                component="CPU",
                message=f"CPU usage is critically high at {metrics.cpu_percent}%",
                root_cause="High compute load from running processes."
            ))
        elif metrics.cpu_percent >= settings.CPU_WARNING_THRESHOLD:
            insights.append(SystemInsight(
                timestamp=metrics.timestamp,
                severity="WARNING",
                component="CPU",
                message=f"CPU usage is elevated at {metrics.cpu_percent}%"
            ))

        # Memory Rules
        if metrics.memory_percent >= settings.MEMORY_CRITICAL_THRESHOLD:
            insights.append(SystemInsight(
                timestamp=metrics.timestamp,
                severity="CRITICAL",
                component="Memory",
                message=f"Memory usage is critically high at {metrics.memory_percent}%",
                root_cause="Potential memory leak or insufficient RAM."
            ))
        elif metrics.memory_percent >= settings.MEMORY_WARNING_THRESHOLD:
            insights.append(SystemInsight(
                timestamp=metrics.timestamp,
                severity="WARNING",
                component="Memory",
                message=f"Memory usage is elevated at {metrics.memory_percent}%"
            ))

        # Disk Rules
        if metrics.disk_percent >= settings.DISK_CRITICAL_THRESHOLD:
            insights.append(SystemInsight(
                timestamp=metrics.timestamp,
                severity="CRITICAL",
                component="Disk",
                message=f"Disk space is critically low ({metrics.disk_percent}% used).",
                root_cause="Storage is nearly full. Action required immediately."
            ))
        elif metrics.disk_percent >= settings.DISK_WARNING_THRESHOLD:
            insights.append(SystemInsight(
                timestamp=metrics.timestamp,
                severity="WARNING",
                component="Disk",
                message=f"Disk space is getting low ({metrics.disk_percent}% used)."
            ))
            
        return insights

class AnomalyDetector:
    def __init__(self):
        # Basic moving average storage (in-memory for simplicity)
        self.history = []
        self.window_size = 10

    def detect(self, metrics: SystemMetricsPayload) -> Optional[SystemInsight]:
        # Simple anomaly detection: if CPU spikes by > 40% compared to average
        if not self.history:
            self.history.append(metrics.cpu_percent)
            return None
            
        avg_cpu = sum(self.history) / len(self.history)
        
        # Update history
        self.history.append(metrics.cpu_percent)
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
        if metrics.cpu_percent > (avg_cpu + 40.0):
            return SystemInsight(
                timestamp=metrics.timestamp,
                severity="WARNING",
                component="CPU",
                message=f"Unusual CPU spike detected. Current: {metrics.cpu_percent}%, Average: {avg_cpu:.1f}%",
                root_cause="Sudden burst in process activity."
            )
        return None

class AnalysisEngine:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.anomaly_detector = AnomalyDetector()

    def analyze(self, metrics: SystemMetricsPayload) -> List[SystemInsight]:
        insights = []
        
        # Run Rule-Based Analysis
        insights.extend(self.rule_engine.evaluate(metrics))
        
        # Run Anomaly Detection
        anomaly = self.anomaly_detector.detect(metrics)
        if anomaly:
            insights.append(anomaly)
            
        return insights
