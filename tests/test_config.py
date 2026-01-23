import os
import pytest


@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to mock environment variables for testing."""
    # Set mock environment variables for testing
    monkeypatch.setenv("JIRA_BASE_URL", "https://jira.example.com")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_TOKEN", "test-jira-token")
    monkeypatch.setenv("GRAYLOG_BASE_URL", "https://graylog.example.com")
    monkeypatch.setenv("GRAYLOG_TOKEN", "test-graylog-token")
    monkeypatch.setenv("GRAYLOG_MCP_BASE_URL", "http://localhost:8000/mcp")
    monkeypatch.setenv("DEFAULT_PROJECTS_PATHS", "/repo/service-a,/repo/service-b")

    # Create a fresh Settings instance with the mocked environment
    from endpoint_auditor.config import Settings
    settings = Settings()

    return settings

def test_jira_configuration(mock_env):
    """Test if Jira configuration loads correctly."""
    assert mock_env.jira_base_url == "https://jira.example.com"
    assert mock_env.jira_email == "test@example.com"
    assert mock_env.jira_token == "test-jira-token"

    # Test the helper function with the settings object
    jira_enabled = bool(
        mock_env.jira_base_url and
        mock_env.jira_email and
        mock_env.jira_token
    )
    assert jira_enabled is True

def test_graylog_configuration(mock_env):
    """Test if Graylog configuration loads correctly."""
    assert mock_env.graylog_base_url == "https://graylog.example.com"
    assert mock_env.graylog_token == "test-graylog-token"
    assert mock_env.graylog_mcp_base_url == "http://localhost:8000/mcp"

    # Test the helper function with the settings object
    graylog_enabled = bool(
        mock_env.graylog_base_url and
        mock_env.graylog_token and
        mock_env.graylog_mcp_base_url
    )
    assert graylog_enabled is True

def test_missing_jira_configuration(monkeypatch):
    """Test if Jira integration is disabled when missing required configuration."""
    monkeypatch.setenv("DEFAULT_PROJECTS_PATHS", "/repo/test")
    # Set to empty strings to override .env file
    monkeypatch.setenv("JIRA_BASE_URL", "")
    monkeypatch.setenv("JIRA_EMAIL", "")
    monkeypatch.setenv("JIRA_TOKEN", "")

    from endpoint_auditor.config import Settings
    settings = Settings()

    # Check that Jira integration would be disabled
    jira_enabled = bool(
        settings.jira_base_url and
        settings.jira_email and
        settings.jira_token
    )
    assert jira_enabled is False

def test_missing_graylog_configuration(monkeypatch):
    """Test if Graylog integration is disabled when missing required configuration."""
    monkeypatch.setenv("DEFAULT_PROJECTS_PATHS", "/repo/test")
    # Set to empty strings to override .env file
    monkeypatch.setenv("GRAYLOG_BASE_URL", "")
    monkeypatch.setenv("GRAYLOG_TOKEN", "")
    monkeypatch.setenv("GRAYLOG_MCP_BASE_URL", "")

    from endpoint_auditor.config import Settings
    settings = Settings()

    # Check that Graylog integration would be disabled
    graylog_enabled = bool(
        settings.graylog_base_url and
        settings.graylog_token and
        settings.graylog_mcp_base_url
    )
    assert graylog_enabled is False

def test_default_projects_paths(mock_env):
    """Test if the default project paths are loaded from the environment correctly."""
    assert mock_env.default_projects_paths == "/repo/service-a,/repo/service-b"

def test_missing_required_default_projects_paths(monkeypatch):
    """Test if Settings initialization fails when required field is missing."""
    from pydantic import ValidationError
    from endpoint_auditor.config import Settings

    # Set to empty string to override .env file - this should fail validation
    monkeypatch.setenv("DEFAULT_PROJECTS_PATHS", "")

    with pytest.raises(ValidationError) as exc_info:
        Settings()

    # Verify the error is about the missing required field
    assert "default_projects_paths" in str(exc_info.value)
