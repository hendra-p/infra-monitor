import yaml
import os
from agent.core.agent import SystemMonitorAgent
from agent.collectors.cpu import CpuCollector
from agent.collectors.memory import MemoryCollector
from agent.collectors.disk import DiskCollector
from agent.collectors.process import ProcessCollector
from agent.clients.api_client import ApiClient
from agent.utils.logger import setup_logger

def load_config(config_path: str = "config.yaml"):
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger = setup_logger("ConfigLoader")
        logger.error(f"Failed to load config from {config_path}: {e}. Using defaults.")
        return {
            "api": {"endpoint": "http://127.0.0.1:8000/api/v1/metrics", "timeout_seconds": 5},
            "agent": {"interval_seconds": 5, "log_level": "INFO"}
        }

if __name__ == "__main__":
    # Resolve config path relative to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, "config.yaml")
    
    config = load_config(config_file)
    
    # Initialize API Client
    api_client = ApiClient(
        endpoint=config["api"]["endpoint"],
        timeout=config["api"].get("timeout_seconds", 5)
    )
    
    # Initialize Collectors
    collectors = [
        CpuCollector(),
        MemoryCollector(),
        DiskCollector(),
        ProcessCollector()
    ]
    
    # Initialize and start Agent
    agent = SystemMonitorAgent(
        collectors=collectors,
        api_client=api_client,
        interval_seconds=config["agent"].get("interval_seconds", 5),
        log_level=config["agent"].get("log_level", "INFO")
    )
    
    agent.start()
