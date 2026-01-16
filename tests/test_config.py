import os
import pytest
from endpoint_auditor.config import settings, is_graylog_enabled, is_jira_enabled

@pytest.fixture
def mock_env():
    """Fixture to mock environment variables for testing."""
    # Set mock environment variables for testing
    os.environ["JIRA_BASE_URL"] = "https://jira.example.com"
    os.environ["JIRA_EMAIL"] = "test@example.com"
    os.environ["JIRA_TOKEN"] = "test-jira-token"
    os.environ["GRAYLOG_BASE_URL"] = "https://graylog.example.com"
    os.environ["GRAYLOG_TOKEN"] = "test-graylog-token"
    os.environ["DEFAULT_PROJECTS_PATHS"] = "/repo/service-a,/repo/service-b"

    # Reload settings after environment variables are mocked
    settings.__init__()

def test_jira_configuration(mock_env):
    """Test if Jira configuration loads correctly."""
    assert settings.jira_base_url == "https://jira.example.com"
    assert settings.jira_email == "test@example.com"
    assert settings.jira_token == "test-jira-token"
    assert is_jira_enabled() is True

def test_graylog_configuration(mock_env):
    """Test if Graylog configuration loads correctly."""
    assert settings.graylog_base_url == "https://graylog.example.com"
    assert settings.graylog_token == "test-graylog-token"
    assert is_graylog_enabled() is True

def test_missing_jira_configuration():
    """Test if Jira integration is disabled when missing required configuration."""
    os.environ["DEFAULT_PROJECTS_PATHS"] = "/repo/test"
    os.environ.pop("JIRA_BASE_URL", None)
    os.environ.pop("JIRA_EMAIL", None)
    os.environ.pop("JIRA_TOKEN", None)
    settings.__init__()
    assert is_jira_enabled() is False

def test_missing_graylog_configuration():
    """Test if Graylog integration is disabled when missing required configuration."""
    os.environ["DEFAULT_PROJECTS_PATHS"] = "/repo/test"
    os.environ.pop("GRAYLOG_BASE_URL", None)
    os.environ.pop("GRAYLOG_TOKEN", None)
    settings.__init__()
    assert is_graylog_enabled() is False

def test_default_projects_paths(mock_env):
    """Test if the default project paths are loaded from the environment correctly."""
    assert settings.default_projects_paths == "/repo/service-a,/repo/service-b"

def test_missing_required_default_projects_paths():
    """Test if Settings initialization fails when required field is missing."""
    from pydantic import ValidationError

    os.environ.pop("DEFAULT_PROJECTS_PATHS", None)

    with pytest.raises(ValidationError) as exc_info:
        from endpoint_auditor.config import Settings
        Settings()

    # Verify the error is about the missing required field
    assert "default_projects_paths" in str(exc_info.value)
