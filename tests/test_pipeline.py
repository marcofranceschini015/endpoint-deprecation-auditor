import pytest
from unittest.mock import patch, AsyncMock
from endpoint_auditor.pipline import run_pipeline
from endpoint_auditor.models import LogExtraction, RuntimeUsage, CodeUsage


@pytest.fixture
def mock_pipeline_components():
    """Fixture to mock all pipeline components for testing."""
    endpoint = "/api/v1/users"
    projects_paths = ["/repo/service-a", "/repo/service-b"]
    days = 30
    log = "User endpoint accessed"

    mock_log_extraction = LogExtraction(
        log_template=["User endpoint accessed"],
        extracted=True
    )

    mock_runtime_usage = RuntimeUsage(
        enabled=True,
        provider="Graylog",
        days=days,
        total_occurrences=42
    )

    mock_code_usage = CodeUsage(
        projects_paths=projects_paths,
        matches_count=3,
        files=["Service.java", "Client.java", "Test.java"]
    )

    mock_report = {
        "metadata": {
            "generated_at": "2026-01-19T10:00:00+00:00",
            "version": "0.1.0"
        },
        "log_extraction": {
            "log_template": ["User endpoint accessed"],
            "extracted": True
        },
        "runtime_usage": {
            "enabled": True,
            "provider": "Graylog",
            "days": days,
            "total_occurrences": 42
        },
        "code_usage": {
            "projects_paths": projects_paths,
            "matches_count": 3,
            "files": ["Service.java", "Client.java", "Test.java"]
        },
        "recommendation": {
            "status": "runtime_usage_detected",
            "rationale": "Runtime log occurrences were detected in the specified time range."
        },
        "warnings": []
    }

    # Setup patches
    with patch("endpoint_auditor.pipline.extract_log") as mock_extract_log, \
         patch("endpoint_auditor.pipline.count_log_occurrences", new_callable=AsyncMock) as mock_count_log, \
         patch("endpoint_auditor.pipline.scan_code_usage") as mock_scan_usage, \
         patch("endpoint_auditor.pipline.generate_base_report") as mock_generate_report:

        # Configure mocks
        mock_extract_log.return_value = mock_log_extraction
        mock_count_log.return_value = mock_runtime_usage
        mock_scan_usage.return_value = mock_code_usage
        mock_generate_report.return_value = mock_report

        yield {
            "endpoint": endpoint,
            "projects_paths": projects_paths,
            "days": days,
            "log": log,
            "mocks": {
                "extract_log": mock_extract_log,
                "count_log": mock_count_log,
                "scan_usage": mock_scan_usage,
                "generate_report": mock_generate_report
            },
            "expected": {
                "log_extraction": mock_log_extraction,
                "runtime_usage": mock_runtime_usage,
                "code_usage": mock_code_usage,
                "report": mock_report
            }
        }


@pytest.mark.asyncio
async def test_run_pipeline_success(mock_pipeline_components):
    """Test the complete pipeline execution with all components working correctly."""
    endpoint = mock_pipeline_components["endpoint"]
    projects_paths = mock_pipeline_components["projects_paths"]
    days = mock_pipeline_components["days"]
    log = mock_pipeline_components["log"]
    mocks = mock_pipeline_components["mocks"]
    expected = mock_pipeline_components["expected"]

    result = await run_pipeline(
        endpoint=endpoint,
        log=log,
        application_name="test-service",
        projects_paths=projects_paths,
        days=days
    )

    mocks["extract_log"].assert_called_once_with(
        log=log
    )

    mocks["count_log"].assert_called_once_with(
        log_extracted=expected["log_extraction"],
        days=days,
        application_name="test-service"
    )

    mocks["scan_usage"].assert_called_once_with(
        endpoint=endpoint,
        projects_paths=projects_paths
    )

    mocks["generate_report"].assert_called_once_with(
        log_extracted=expected["log_extraction"],
        runtime_usage=expected["runtime_usage"],
        code_usage=expected["code_usage"]
    )

    assert result == expected["report"]
    assert result["runtime_usage"]["total_occurrences"] == 42
    assert result["code_usage"]["matches_count"] == 3
    assert result["recommendation"]["status"] == "runtime_usage_detected"
