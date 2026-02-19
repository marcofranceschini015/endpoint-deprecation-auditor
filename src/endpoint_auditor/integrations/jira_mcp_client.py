from atlassian import Jira

from endpoint_auditor.config import settings


class JiraClient:
    """
    Client for interacting with the Jira REST API.

    Uses atlassian-python-api under the hood (the same library mcp-atlassian wraps).
    """

    def __init__(self):
        """Initialize the Jira client with configuration from settings."""
        try:
            self._jira = Jira(
                url=settings.jira_base_url,
                username=settings.jira_email,
                password=settings.jira_token,
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Jira client: {e}")

    def add_comment(self, issue_key: str, comment: str) -> dict:
        """
        Add a comment to a Jira issue.

        Args:
            issue_key: Jira issue key (e.g. 'PROJ-123')
            comment: Comment text in Jira wiki markup format

        Returns:
            The response from the Jira API as a dict
        """
        return self._jira.issue_add_comment(issue_key, comment)
