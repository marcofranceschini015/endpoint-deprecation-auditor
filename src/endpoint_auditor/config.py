import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Configuration settings for the Endpoint Deprecation Auditor tool.
    Environment variables are loaded automatically from .env or system environment.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Jira Configuration
    jira_base_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_token: Optional[str] = None

    # Graylog Configuration
    graylog_base_url: Optional[str] = None
    graylog_token: Optional[str] = None
    graylog_mcp_base_url: Optional[str] = None

    # Project paths for scanning codebase
    default_projects_paths: str

    @field_validator('default_projects_paths')
    @classmethod
    def validate_default_projects_paths(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('default_projects_paths cannot be empty')
        return v


settings = Settings()


def is_graylog_enabled() -> bool:
    """Returns whether Graylog integration is enabled based on configuration."""
    return bool(settings.graylog_base_url and settings.graylog_token and settings.graylog_mcp_base_url)


def is_jira_enabled() -> bool:
    """Returns whether Jira integration is enabled based on configuration."""
    return bool(settings.jira_base_url and settings.jira_email and settings.jira_token)
