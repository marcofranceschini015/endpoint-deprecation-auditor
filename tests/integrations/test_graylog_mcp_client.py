import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch

from endpoint_auditor.integrations.graylog_mcp_client import GraylogMCPClient, BearerAuth


class TestBearerAuth:
    """Test suite for BearerAuth class."""
    
    def test_bearer_auth_initialization(self):
        """Test BearerAuth initializes with correct attributes."""
        auth = BearerAuth(
            token="test-token",
            graylog_base_url="https://graylog.example.com",
            graylog_token="graylog-token"
        )
        
        assert auth.token == "test-token"
        assert auth.graylog_base_url == "https://graylog.example.com"
        assert auth.graylog_token == "graylog-token"
    
    def test_bearer_auth_call_adds_headers(self):
        """Test BearerAuth adds correct headers to request."""
        auth = BearerAuth(
            token="test-token",
            graylog_base_url="https://graylog.example.com",
            graylog_token="graylog-token"
        )
        
        mock_request = MagicMock()
        mock_request.headers = {}
        
        result = auth(mock_request)
        
        assert result.headers["Authorization"] == "Bearer test-token"
        assert result.headers["X-GRAYLOG-API-BASE-URL"] == "https://graylog.example.com"
        assert result.headers["X-GRAYLOG-API-TOKEN"] == "graylog-token"


class TestGraylogMCPClient:
    """Test suite for GraylogMCPClient class."""
    
    @patch('endpoint_auditor.integrations.graylog_mcp_client.Client')
    @patch('endpoint_auditor.integrations.graylog_mcp_client.settings')
    def test_client_initialization_success(self, mock_settings, mock_client_class):
        """Test successful client initialization."""
        mock_settings.graylog_token = "test-token"
        mock_settings.graylog_base_url = "https://graylog.example.com"
        mock_settings.graylog_mcp_base_url = "https://mcp.example.com"
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        client = GraylogMCPClient()
        
        assert client._client is mock_client
        mock_client_class.assert_called_once()
        
    @patch('endpoint_auditor.integrations.graylog_mcp_client.Client')
    @patch('endpoint_auditor.integrations.graylog_mcp_client.settings')
    def test_client_initialization_failure(self, mock_settings, mock_client_class):
        """Test client initialization handles exceptions."""
        mock_settings.graylog_token = "test-token"
        mock_settings.graylog_base_url = "https://graylog.example.com"
        mock_settings.graylog_mcp_base_url = "https://mcp.example.com"
        
        mock_client_class.side_effect = Exception("Connection error")
        
        with pytest.raises(ValueError, match="Failed to initialize Graylog MCP client"):
            GraylogMCPClient()
    
    @pytest.mark.asyncio
    @patch('endpoint_auditor.integrations.graylog_mcp_client.Client')
    @patch('endpoint_auditor.integrations.graylog_mcp_client.settings')
    async def test_find_stream_by_name_success(self, mock_settings, mock_client_class):
        """Test finding stream by name when stream exists."""
        mock_settings.graylog_token = "test-token"
        mock_settings.graylog_base_url = "https://graylog.example.com"
        mock_settings.graylog_mcp_base_url = "https://mcp.example.com"
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        streams_data = [
            {"id": "stream-1", "title": "Production Logs"},
            {"id": "stream-2", "title": "Development Logs"},
            {"id": "stream-3", "title": "Test Logs"}
        ]
        
        mock_result = MagicMock()
        mock_result.data = json.dumps(streams_data)
        mock_client.call_tool = AsyncMock(return_value=mock_result)
        
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        client = GraylogMCPClient()
        stream_id = await client._find_stream_by_name("Development Logs")
        
        assert stream_id == "stream-2"
        mock_client.call_tool.assert_called_once_with("get_streams", {})
    
    @pytest.mark.asyncio
    @patch('endpoint_auditor.integrations.graylog_mcp_client.Client')
    @patch('endpoint_auditor.integrations.graylog_mcp_client.settings')
    async def test_find_stream_by_name_not_found(self, mock_settings, mock_client_class):
        """Test finding stream by name when stream does not exist."""
        mock_settings.graylog_token = "test-token"
        mock_settings.graylog_base_url = "https://graylog.example.com"
        mock_settings.graylog_mcp_base_url = "https://mcp.example.com"
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        streams_data = [
            {"id": "stream-1", "title": "Production Logs"},
            {"id": "stream-2", "title": "Development Logs"}
        ]
        
        mock_result = MagicMock()
        mock_result.data = json.dumps(streams_data)
        mock_client.call_tool = AsyncMock(return_value=mock_result)
        
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        client = GraylogMCPClient()
        
        with pytest.raises(ValueError, match="Stream 'NonExistent' not found"):
            await client._find_stream_by_name("NonExistent")
    
    @pytest.mark.asyncio
    @patch('endpoint_auditor.integrations.graylog_mcp_client.Client')
    @patch('endpoint_auditor.integrations.graylog_mcp_client.settings')
    async def test_search_logs_with_results(self, mock_settings, mock_client_class):
        """Test searching logs returns correct count."""
        mock_settings.graylog_token = "test-token"
        mock_settings.graylog_base_url = "https://graylog.example.com"
        mock_settings.graylog_mcp_base_url = "https://mcp.example.com"
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        search_data = {
            "datarows": [
                {"message": "Log 1", "caseId": "123", "timestamp": "2024-01-01"},
                {"message": "Log 2", "caseId": "456", "timestamp": "2024-01-02"},
                {"message": "Log 3", "caseId": "789", "timestamp": "2024-01-03"}
            ]
        }
        
        mock_result = MagicMock()
        mock_result.data = json.dumps(search_data)
        mock_client.call_tool = AsyncMock(return_value=mock_result)
        
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        client = GraylogMCPClient()
        count = await client._search_logs("stream-123", "test query", 7)
        
        assert count == 3
        mock_client.call_tool.assert_called_once_with("search_messages_relative", {
            "stream_id": "stream-123",
            "lucene_query": "test query",
            "range_in_seconds": 604800,  # 7 days in seconds
            "size": 300,
            "fields": ["message", "caseId", "timestamp"]
        })
    
    @pytest.mark.asyncio
    @patch('endpoint_auditor.integrations.graylog_mcp_client.Client')
    @patch('endpoint_auditor.integrations.graylog_mcp_client.settings')
    async def test_search_logs_no_results(self, mock_settings, mock_client_class):
        """Test searching logs with no results returns 0."""
        mock_settings.graylog_token = "test-token"
        mock_settings.graylog_base_url = "https://graylog.example.com"
        mock_settings.graylog_mcp_base_url = "https://mcp.example.com"
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        search_data = {"datarows": []}
        
        mock_result = MagicMock()
        mock_result.data = json.dumps(search_data)
        mock_client.call_tool = AsyncMock(return_value=mock_result)
        
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        client = GraylogMCPClient()
        count = await client._search_logs("stream-123", "nonexistent query", 30)
        
        assert count == 0
    
    @pytest.mark.asyncio
    @patch('endpoint_auditor.integrations.graylog_mcp_client.Client')
    @patch('endpoint_auditor.integrations.graylog_mcp_client.settings')
    async def test_get_log_count_by_stream_name_integration(self, mock_settings, mock_client_class):
        """Test complete flow of getting log count by stream name."""
        mock_settings.graylog_token = "test-token"
        mock_settings.graylog_base_url = "https://graylog.example.com"
        mock_settings.graylog_mcp_base_url = "https://mcp.example.com"
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock get_streams response
        streams_data = [
            {"id": "prod-stream-id", "title": "Production Logs"}
        ]
        mock_streams_result = MagicMock()
        mock_streams_result.data = json.dumps(streams_data)
        
        # Mock search_messages_relative response
        search_data = {
            "datarows": [
                {"message": "Log 1"},
                {"message": "Log 2"},
                {"message": "Log 3"},
                {"message": "Log 4"},
                {"message": "Log 5"}
            ]
        }
        mock_search_result = MagicMock()
        mock_search_result.data = json.dumps(search_data)
        
        # Configure call_tool to return different results based on call
        async def call_tool_side_effect(tool_name, params):
            if tool_name == "get_streams":
                return mock_streams_result
            elif tool_name == "search_messages_relative":
                return mock_search_result
        
        mock_client.call_tool = AsyncMock(side_effect=call_tool_side_effect)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        client = GraylogMCPClient()
        count = await client.get_log_count_by_stream_name(
            stream_name="Production Logs",
            query='"Error occurred"',
            days=14
        )
        
        assert count == 5
        assert mock_client.call_tool.call_count == 2