import time
from typing import List
from datetime import datetime
from agent.core.base import MetricCollector
from agent.clients.api_client import ApiClient
from agent.models.metrics import SystemMetricsPayload
from agent.utils.logger import setup_logger

class SystemMonitorAgent:
    def __init__(
        self, 
        collectors: List[MetricCollector], 
        api_client: ApiClient,
        interval_seconds: int = 5,
        log_level: str = "INFO"
    ):
        self.collectors = collectors
        self.api_client = api_client
        self.interval_seconds = interval_seconds
        self.logger = setup_logger("SystemMonitorAgent", log_level)
        self.running = False

    def start(self):
        self.running = True
        self.logger.info(f"Agent started. Collecting metrics every {self.interval_seconds} seconds.")
        
        try:
            while self.running:
                self._collect_and_send()
                time.sleep(self.interval_seconds)
        except KeyboardInterrupt:
            self.logger.info("Agent stopped by user.")
            self.stop()

    def stop(self):
        self.running = False

    def _collect_and_send(self):
        payload = SystemMetricsPayload(timestamp=datetime.utcnow().isoformat())
        
        # Collect metrics from all registered collectors
        for collector in self.collectors:
            try:
                collector.collect(payload)
            except Exception as e:
                self.logger.error(f"Error collecting metrics with {collector.__class__.__name__}: {e}")
        
        # Send payload
        # Pydantic v2 uses model_dump, v1 uses dict.
        try:
            payload_dict = payload.model_dump()
        except AttributeError:
            payload_dict = payload.dict()
            
        self.api_client.send_metrics(payload_dict)
