import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuration settings for the Endpoint Deprecation Auditor tool.
    Environment variables are loaded automatically from .env or system environment.
    """

    # Jira Configuration
    jira_base_url: Optional[str] = Field(None, env="JIRA_BASE_URL")
    jira_email: Optional[str] = Field(None, env="JIRA_EMAIL")
    jira_token: Optional[str] = Field(None, env="JIRA_TOKEN")

    # Graylog Configuration
    graylog_base_url: Optional[str] = Field(None, env="GRAYLOG_BASE_URL")
    graylog_token: Optional[str] = Field(None, env="GRAYLOG_TOKEN")

    # Project paths for scanning codebase
    default_projects_paths: Optional[str] = Field(
        None, env="DEFAULT_PROJECTS_PATHS"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def is_graylog_enabled() -> bool:
    """Returns whether Graylog integration is enabled based on configuration."""
    return bool(settings.graylog_base_url and settings.graylog_token)


def is_jira_enabled() -> bool:
    """Returns whether Jira integration is enabled based on configuration."""
    return bool(settings.jira_base_url and settings.jira_email and settings.jira_token)
