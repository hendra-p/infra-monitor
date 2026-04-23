from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "InfraMonitor SRE"
    API_V1_STR: str = "/api/v1"
    
    # Database: Switch to PostgreSQL when Docker is ready
    # PostgreSQL: "postgresql://inframon:inframon_secret@localhost:5432/infra_monitor"
    # SQLite (fallback): "sqlite:///./infra_monitor.db"
    DATABASE_URL: str = "sqlite:///./infra_monitor.db"
    
    # Alerting thresholds
    CPU_WARNING_THRESHOLD: float = 80.0
    CPU_CRITICAL_THRESHOLD: float = 95.0
    MEMORY_WARNING_THRESHOLD: float = 85.0
    MEMORY_CRITICAL_THRESHOLD: float = 95.0
    DISK_WARNING_THRESHOLD: float = 85.0
    DISK_CRITICAL_THRESHOLD: float = 95.0

    # Data retention (14 days)
    RETENTION_DAYS: int = 14

    class Config:
        env_file = ".env"

settings = Settings()
