import requests
import logging
from typing import Dict, Any

logger = logging.getLogger("ApiClient")

class ApiClient:
    def __init__(self, endpoint: str, timeout: int = 5):
        self.endpoint = endpoint
        self.timeout = timeout
        self.session = requests.Session()

    def send_metrics(self, payload_dict: Dict[str, Any]) -> bool:
        try:
            response = self.session.post(
                self.endpoint, 
                json=payload_dict, 
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.debug(f"Successfully sent metrics to {self.endpoint}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send metrics: {e}")
            return False
