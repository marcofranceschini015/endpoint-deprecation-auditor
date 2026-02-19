import pytest
from unittest.mock import MagicMock, patch

from endpoint_auditor.integrations.jira_mcp_client import JiraClient


class TestJiraClient:
    """Test suite for JiraClient class."""

    @patch('endpoint_auditor.integrations.jira_mcp_client.Jira')
    @patch('endpoint_auditor.integrations.jira_mcp_client.settings')
    def test_client_initialization_success(self, mock_settings, mock_jira_class):
        """Test successful client initialization."""
        mock_settings.jira_token = "test-token"
        mock_settings.jira_base_url = "https://jira.example.com"
        mock_settings.jira_email = "user@example.com"

        mock_jira = MagicMock()
        mock_jira_class.return_value = mock_jira

        client = JiraClient()

        assert client._jira is mock_jira
        mock_jira_class.assert_called_once_with(
            url="https://jira.example.com",
            username="user@example.com",
            password="test-token",
        )

    @patch('endpoint_auditor.integrations.jira_mcp_client.Jira')
    @patch('endpoint_auditor.integrations.jira_mcp_client.settings')
    def test_client_initialization_failure(self, mock_settings, mock_jira_class):
        """Test client initialization handles exceptions."""
        mock_settings.jira_token = "test-token"
        mock_settings.jira_base_url = "https://jira.example.com"
        mock_settings.jira_email = "user@example.com"

        mock_jira_class.side_effect = Exception("Connection error")

        with pytest.raises(ValueError, match="Failed to initialize Jira client"):
            JiraClient()

    @patch('endpoint_auditor.integrations.jira_mcp_client.Jira')
    @patch('endpoint_auditor.integrations.jira_mcp_client.settings')
    def test_add_comment_success(self, mock_settings, mock_jira_class):
        """Test adding a comment to a Jira issue."""
        mock_settings.jira_token = "test-token"
        mock_settings.jira_base_url = "https://jira.example.com"
        mock_settings.jira_email = "user@example.com"

        mock_jira = MagicMock()
        mock_jira_class.return_value = mock_jira

        response_data = {"id": "12345", "body": "Test comment"}
        mock_jira.issue_add_comment.return_value = response_data

        client = JiraClient()
        result = client.add_comment(
            issue_key="PROJ-123",
            comment="h2. Audit Report\nSome content"
        )

        assert result == response_data
        mock_jira.issue_add_comment.assert_called_once_with(
            "PROJ-123",
            "h2. Audit Report\nSome content",
        )

    @patch('endpoint_auditor.integrations.jira_mcp_client.Jira')
    @patch('endpoint_auditor.integrations.jira_mcp_client.settings')
    def test_add_comment_propagates_exception(self, mock_settings, mock_jira_class):
        """Test that API errors propagate from add_comment."""
        mock_settings.jira_token = "test-token"
        mock_settings.jira_base_url = "https://jira.example.com"
        mock_settings.jira_email = "user@example.com"

        mock_jira = MagicMock()
        mock_jira_class.return_value = mock_jira
        mock_jira.issue_add_comment.side_effect = Exception("Jira API error")

        client = JiraClient()

        with pytest.raises(Exception, match="Jira API error"):
            client.add_comment(issue_key="PROJ-123", comment="test")
