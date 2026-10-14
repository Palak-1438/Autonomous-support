from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    app_name: str = "autonomous-support"
    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "dev-only-change-me"
    llm_mode: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_classifier_model: str = "gpt-4o-mini"
    openai_base_url: str = ""

    database_url: str = "sqlite+pysqlite:///./data/support.db"
    redis_url: str = "redis://localhost:6379/0"
    use_redis: bool = False

    demo_tenant_id: str = "tenant_demo"
    demo_customer_api_key: str = "demo_customer_key"
    demo_agent_api_key: str = "demo_agent_key"
    demo_admin_api_key: str = "demo_admin_key"

    max_retries: int = 2
    max_specialist_handoffs: int = 3
    rate_limit_per_minute: int = 60
    page_size_default: int = 20
    page_size_max: int = 100

    otel_exporter_otlp_endpoint: str = ""
    otel_service_name: str = "autonomous-support"

    configs_dir: Path = Field(default=ROOT / "configs")

    @property
    def domains_dir(self) -> Path:
        return self.configs_dir / "domains"

    @property
    def knowledge_dir(self) -> Path:
        return self.configs_dir / "knowledge"

    @property
    def tenants_dir(self) -> Path:
        return self.configs_dir / "tenants"

    @property
    def openai_enabled(self) -> bool:
        return self.llm_mode.lower() == "openai"


@lru_cache
def get_settings() -> Settings:
    return Settings()
