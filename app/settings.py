from functools import lru_cache
from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator
from pydantic_settings import BaseSettings

from formbricks.settings import FormbricksConfig
from grist.settings import GristConfig
from notification.settings import MailConfig


# ========================
# Configuration Management
# ========================


def log_level_validator(value: str) -> str:
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if value.upper() not in valid_levels:
        raise ValueError(f'Log level must be one of {valid_levels}')
    return value.upper()


class ServerConfig(BaseModel):

    listen: str = Field(
        default="0.0.0.0",
        description="listen address"
    )
    port: int = Field(
        default=8000,
        description="listen port",
        ge=1,
        le=65535
    )
    reload: bool = Field(
        default=False,
        description="auto reload on changes"
    )
    workers: int = Field(
        default=1,
        description="number workers",
        ge=1
    )


class LoggingConfig(BaseModel):
    """logging configuration"""

    level: Annotated[str, AfterValidator(log_level_validator)] = Field(
        default="INFO",
        description="Log Level"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log Format"
    )


class Settings(BaseSettings):

    debug: bool = Field(default=False, description="Debug mode")

    # Server Config
    server: ServerConfig = Field(default_factory=ServerConfig)

    # Webhook Config
    formbricks: FormbricksConfig = FormbricksConfig()

    # Grist Config
    grist: GristConfig = GristConfig()

    # Logging Config
    logging: LoggingConfig = LoggingConfig()

    # eMail Config
    mail: MailConfig = MailConfig()

    class Config:
        env_file = (".env", ".env.local")
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"  # permits SERVER__HOST=localhost
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
