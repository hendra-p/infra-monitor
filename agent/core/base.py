from abc import ABC, abstractmethod
from agent.models.metrics import SystemMetricsPayload

class MetricCollector(ABC):
    """
    Abstract Base Class for all metric collectors.
    Enforces the collect method to be implemented.
    """
    
    @abstractmethod
    def collect(self, payload: SystemMetricsPayload) -> None:
        """
        Collects specific metrics and updates the payload object.
        """
        pass
