import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from endpoint_auditor.integrations.graylog_service import count_log_occurrences, _build_query
from endpoint_auditor.models import LogExtraction, RuntimeUsage


@pytest.mark.asyncio
@patch('endpoint_auditor.integrations.graylog_service.is_graylog_enabled')
async def test_graylog_not_enabled_returns_default_runtime_usage(mock_is_enabled):
    """Test that when Graylog is not enabled, return default RuntimeUsage."""
    mock_is_enabled.return_value = False

    log_extracted = LogExtraction(
        log_template=["Downloading Acceptance Document", "for case:"],
        extracted=True
    )

    actual = await count_log_occurrences(
        log_extracted=log_extracted,
        days=7,
        application_name="test-stream"
    )
    
    expected = RuntimeUsage(
        enabled=False,
        provider=None,
        days=7,
        total_occurrences=None
    )

    assert actual == expected


@pytest.mark.asyncio
@patch('endpoint_auditor.integrations.graylog_service.is_graylog_enabled')
async def test_no_log_extracted_returns_default_runtime_usage(mock_is_enabled):
    """Test that when log is not extracted, return default RuntimeUsage."""
    mock_is_enabled.return_value = True

    log_extracted = LogExtraction(
        log_template=["Some log"],
        extracted=False
    )

    actual = await count_log_occurrences(
        log_extracted=log_extracted,
        days=7,
        application_name="test-stream"
    )

    expected = RuntimeUsage(
        enabled=False,
        provider=None,
        days=7,
        total_occurrences=None
    )

    assert actual == expected


@pytest.mark.asyncio
@patch('endpoint_auditor.integrations.graylog_service.is_graylog_enabled')
async def test_log_template_empty_returns_default_runtime_usage(mock_is_enabled):
    """Test that when log_template is empty, return default RuntimeUsage."""
    mock_is_enabled.return_value = True

    log_extracted = LogExtraction(
        log_template=[],
        extracted=True
    )

    actual = await count_log_occurrences(
        log_extracted=log_extracted,
        days=7,
        application_name="test-stream"
    )

    expected = RuntimeUsage(
        enabled=False,
        provider=None,
        days=7,
        total_occurrences=None
    )

    assert actual == expected


@pytest.mark.asyncio
@patch('endpoint_auditor.integrations.graylog_service.is_graylog_enabled')
@patch('endpoint_auditor.integrations.graylog_service.GraylogMCPClient')
async def test_client_throws_exception_returns_default_runtime_usage(mock_client_class, mock_is_enabled):
    """Test that when client throws exception, return default RuntimeUsage."""
    mock_is_enabled.return_value = True

    mock_client = MagicMock()
    mock_client.get_log_count_by_stream_name = AsyncMock(side_effect=Exception("Connection error"))
    mock_client_class.return_value = mock_client

    log_extracted = LogExtraction(
        log_template=["Downloading Acceptance Document", "for case:"],
        extracted=True
    )

    actual = await count_log_occurrences(
        log_extracted=log_extracted,
        days=7,
        application_name="test-stream"
    )

    expected = RuntimeUsage(
        enabled=False,
        provider=None,
        days=7,
        total_occurrences=None
    )

    assert actual == expected


@pytest.mark.asyncio
@patch('endpoint_auditor.integrations.graylog_service.is_graylog_enabled')
@patch('endpoint_auditor.integrations.graylog_service.GraylogMCPClient')
async def test_success_with_log_extracted_returns_correct_runtime_usage(mock_client_class, mock_is_enabled):
    """Test successful log count with proper query construction and result."""
    mock_is_enabled.return_value = True

    mock_client = MagicMock()
    mock_client.get_log_count_by_stream_name = AsyncMock(return_value=42)
    mock_client_class.return_value = mock_client

    log_extracted = LogExtraction(
        log_template=["Downloading Acceptance Document", "for case:"],
        extracted=True
    )

    actual = await count_log_occurrences(
        log_extracted=log_extracted,
        days=7,
        application_name="test-stream"
    )

    expected_query = '"Downloading Acceptance Document" AND "for case:"'
    mock_client.get_log_count_by_stream_name.assert_called_once_with(
        stream_name="test-stream",
        query=expected_query,
        days=7
    )

    expected = RuntimeUsage(
        enabled=True,
        provider="Graylog",
        days=7,
        total_occurrences=42
    )

    assert actual == expected


def test_build_query_with_multiple_templates():
    """Test _build_query function with multiple log templates."""
    log_template = ["Downloading Acceptance Document", "for case:"]

    query = _build_query(log_template)

    assert query == '"Downloading Acceptance Document" AND "for case:"'


def test_build_query_with_single_template():
    """Test _build_query function with single log template."""
    log_template = ["Single log entry"]

    query = _build_query(log_template)

    assert query == '"Single log entry"'


def test_build_query_with_empty_list():
    """Test _build_query function with empty list."""
    log_template = []

    query = _build_query(log_template)

    assert query == ""
