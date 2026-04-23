import logging
from typing import List
from backend.schemas.api_models import SystemInsight

logger = logging.getLogger("AlertManager")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class AlertManager:
    def __init__(self):
        pass

    def process_insights(self, insights: List[SystemInsight]):
        for insight in insights:
            self._dispatch(insight)

    def _dispatch(self, insight: SystemInsight):
        """
        Dispatches alerts based on severity. Extensible for Email/Slack.
        """
        log_message = f"[{insight.component}] {insight.message} (Root Cause: {insight.root_cause or 'N/A'})"
        
        if insight.severity == "CRITICAL":
            logger.error(f"🚨 CRITICAL ALERT: {log_message}")
            # TODO: Integrate PagerDuty, Slack, or Email here
        elif insight.severity == "WARNING":
            logger.warning(f"⚠️ WARNING: {log_message}")
        else:
            logger.info(f"ℹ️ INFO: {log_message}")
