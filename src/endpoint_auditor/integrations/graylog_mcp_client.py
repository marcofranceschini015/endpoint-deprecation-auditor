from typing import Optional
from fastmcp import Client
from fastmcp.transports import StreamableHttpTransport

from endpoint_auditor.config import settings


class GraylogMCPClient:
    """
    Client for interacting with Graylog via MCP (Model Context Protocol).

    Uses FastMCP to communicate with Graylog API endpoints.
    """

    def __init__(self):
        """Initialize the Graylog MCP client with configuration from settings."""
        self._client: Optional[Client] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Create and configure the MCP client if Graylog is enabled."""
        try:
            transport = StreamableHttpTransport(
                url=f"{settings.graylog_mcp_base_url}",
                headers={
                    "Authorization": f"Bearer {settings.graylog_token}",
                    "X-GRAYLOG-API-BASE-URL": settings.graylog_base_url,
                    "X-GRAYLOG-API-TOKEN": settings.graylog_token,
                },
            )
            self._client = Client(transport)
        except Exception as e:
            raise ValueError(f"Failed to initialize Graylog MCP client: {e}")
