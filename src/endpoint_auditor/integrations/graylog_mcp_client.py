from typing import Optional
import json
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

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
                url=settings.graylog_mcp_base_url,
                headers={
                    "Authorization": f"Bearer {settings.graylog_token}",
                    "X-GRAYLOG-API-BASE-URL": settings.graylog_base_url,
                    "X-GRAYLOG-API-TOKEN": settings.graylog_token,
                },
            )
            self._client = Client(transport)
        except Exception as e:
            raise ValueError(f"Failed to initialize Graylog MCP client: {e}")


    async def get_log_count_by_stream_name(self, stream_name: str, query: str, days: int) -> int:
        """
        Get log count by stream name in a single connection.

        Args:
            stream_name: Name of the stream
            query: Lucene query
            days: Number of days to search

        Returns:
            Number of log occurrences
        """
        async with self._client:
            stream_id = await self._find_stream_by_name(stream_name)
            return await self._search_logs(stream_id, query, days)


    async def _find_stream_by_name(self, stream_name: str) -> str:
        """
        Find stream ID by name.

        Args:
            stream_name: Name of the stream to find

        Returns:
            Stream ID

        Raises:
            ValueError: If stream not found
        """
        streams_result = await self._client.call_tool("get_streams", {})
        streams_data = json.loads(getattr(streams_result, "data", streams_result))

        for stream in streams_data:
            if stream["title"] == stream_name:
                return stream["id"]

        raise ValueError(f"Stream '{stream_name}' not found")


    async def _search_logs(self, stream_id: str, query: str, days: int) -> int:
        """
        Search logs in a stream and count occurrences.

        Args:
            stream_id: ID of the stream
            query: Lucene query
            days: Number of days to search

        Returns:
            Number of log occurrences
        """
        range_in_seconds = days * 24 * 60 * 60
        search_result = await self._client.call_tool("search_messages_relative", {
            "stream_id": stream_id,
            "lucene_query": query,
            "range_in_seconds": range_in_seconds,
            "size": 300,
            "fields": ["message", "caseId", "timestamp"]
        })

        search_data = json.loads(getattr(search_result, "data", search_result))
        return len(search_data.get("datarows", []))
