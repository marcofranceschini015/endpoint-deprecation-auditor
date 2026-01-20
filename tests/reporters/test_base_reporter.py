import pytest
from unittest.mock import patch

from endpoint_auditor.reporters.base_reporter import generate_base_report, _generate_warnings
from endpoint_auditor.models import EndpointInfo, LogExtraction, RuntimeUsage, CodeUsage, HttpMethod


@pytest.fixture
def mock_endpoint_info():
    """Fixture for mock endpoint info."""
    return EndpointInfo(
        endpoint_path="/api/v1/users",
        controller_file="/repo/UserController.java",
        http_method=HttpMethod.GET,
        handler_method="getUsers"
    )


@pytest.fixture
def mock_log_extracted():
    """Fixture for successfully extracted log."""
    return LogExtraction(
        log_template="User endpoint accessed: {}",
        extracted=True
    )


@pytest.fixture
def mock_log_not_extracted():
    """Fixture for failed log extraction."""
    return LogExtraction(
        log_template=None,
        extracted=False
    )


def test_generate_report_runtime_usage_detected(mock_endpoint_info, mock_log_extracted):
    """Test recommendation when runtime usage is detected (line 38-42)."""
    runtime_usage = RuntimeUsage(
        enabled=True,
        provider="Graylog",
        days=30,
        total_occurrences=42
    )

    code_usage = CodeUsage(
        projects_paths=["/repo/service-a"],
        matches_count=0,
        files=[]
    )

    with patch("endpoint_auditor.reporters.base_reporter._utc_now_iso") as mock_time:
        mock_time.return_value = "2026-01-19T10:00:00+00:00"

        result = generate_base_report(
            endpoint_info=mock_endpoint_info,
            log_extracted=mock_log_extracted,
            runtime_usage=runtime_usage,
            code_usage=code_usage
        )

    assert result["recommendation"]["status"] == "runtime_usage_detected"
    assert result["recommendation"]["rationale"] == "Runtime log occurrences were detected in the specified time range."
    assert result["runtime_usage"]["total_occurrences"] == 42


def test_generate_report_still_referenced_in_code(mock_endpoint_info, mock_log_extracted):
    """Test recommendation when code references are found (line 43-47)."""
    runtime_usage = RuntimeUsage(
        enabled=True,
        provider="Graylog",
        days=30,
        total_occurrences=0
    )

    code_usage = CodeUsage(
        projects_paths=["/repo/service-a", "/repo/service-b"],
        matches_count=5,
        files=["Service.java", "Client.java"]
    )

    with patch("endpoint_auditor.reporters.base_reporter._utc_now_iso") as mock_time:
        mock_time.return_value = "2026-01-19T10:00:00+00:00"

        result = generate_base_report(
            endpoint_info=mock_endpoint_info,
            log_extracted=mock_log_extracted,
            runtime_usage=runtime_usage,
            code_usage=code_usage
        )

    assert result["recommendation"]["status"] == "still_referenced_in_code"
    assert result["recommendation"]["rationale"] == "Static references to the endpoint were found in the scanned codebases."
    assert result["code_usage"]["matches_count"] == 5


def test_generate_report_candidate_for_deprecation(mock_endpoint_info, mock_log_extracted):
    """Test recommendation when no usage is detected (line 48-52)."""
    runtime_usage = RuntimeUsage(
        enabled=True,
        provider="Graylog",
        days=30,
        total_occurrences=0
    )

    code_usage = CodeUsage(
        projects_paths=["/repo/service-a"],
        matches_count=0,
        files=[]
    )

    with patch("endpoint_auditor.reporters.base_reporter._utc_now_iso") as mock_time:
        mock_time.return_value = "2026-01-19T10:00:00+00:00"

        result = generate_base_report(
            endpoint_info=mock_endpoint_info,
            log_extracted=mock_log_extracted,
            runtime_usage=runtime_usage,
            code_usage=code_usage
        )

    assert result["recommendation"]["status"] == "candidate_for_deprecation"
    assert result["recommendation"]["rationale"] == "No runtime usage detected and no static references found in scanned codebases."
    assert result["runtime_usage"]["total_occurrences"] == 0
    assert result["code_usage"]["matches_count"] == 0


def test_generate_report_runtime_disabled_with_code_usage(mock_endpoint_info, mock_log_extracted):
    """Test recommendation when runtime is disabled but code usage exists."""
    runtime_usage = RuntimeUsage(
        enabled=False,
        provider=None,
        days=30,
        total_occurrences=None
    )

    code_usage = CodeUsage(
        projects_paths=["/repo/service-a"],
        matches_count=3,
        files=["Test.java"]
    )

    with patch("endpoint_auditor.reporters.base_reporter._utc_now_iso") as mock_time:
        mock_time.return_value = "2026-01-19T10:00:00+00:00"

        result = generate_base_report(
            endpoint_info=mock_endpoint_info,
            log_extracted=mock_log_extracted,
            runtime_usage=runtime_usage,
            code_usage=code_usage
        )

    assert result["recommendation"]["status"] == "still_referenced_in_code"
    assert result["code_usage"]["matches_count"] == 3


def test_generate_report_structure(mock_endpoint_info, mock_log_extracted):
    """Test that the report has the correct structure with all required fields."""
    runtime_usage = RuntimeUsage(
        enabled=True,
        provider="Graylog",
        days=30,
        total_occurrences=10
    )

    code_usage = CodeUsage(
        projects_paths=["/repo/service-a"],
        matches_count=2,
        files=["File.java"]
    )

    with patch("endpoint_auditor.reporters.base_reporter._utc_now_iso") as mock_time:
        mock_time.return_value = "2026-01-19T10:00:00+00:00"

        result = generate_base_report(
            endpoint_info=mock_endpoint_info,
            log_extracted=mock_log_extracted,
            runtime_usage=runtime_usage,
            code_usage=code_usage
        )

    assert "metadata" in result
    assert result["metadata"]["generated_at"] == "2026-01-19T10:00:00+00:00"
    assert result["metadata"]["version"] == "0.1.0"
    assert "endpoint" in result
    assert "log_extraction" in result
    assert "runtime_usage" in result
    assert "code_usage" in result
    assert "recommendation" in result
    assert "warnings" in result
    assert result["warnings"] == []


def test_generate_report_with_warnings(mock_endpoint_info, mock_log_not_extracted):
    """Test that warnings are included in the report when issues occur."""
    runtime_usage = RuntimeUsage(
        enabled=False,
        provider=None,
        days=30,
        total_occurrences=None
    )

    code_usage = CodeUsage(
        projects_paths=["/repo/service-a"],
        matches_count=0,
        files=[]
    )

    with patch("endpoint_auditor.reporters.base_reporter._utc_now_iso") as mock_time:
        mock_time.return_value = "2026-01-19T10:00:00+00:00"

        result = generate_base_report(
            endpoint_info=mock_endpoint_info,
            log_extracted=mock_log_not_extracted,
            runtime_usage=runtime_usage,
            code_usage=code_usage
        )

    assert len(result["warnings"]) == 2
    assert "Problems while extracting logs: Skipping log analysis" in result["warnings"]
    assert "Problems while connecting to log extractor: Skipping log analysis" in result["warnings"]
    assert result["recommendation"]["status"] == "candidate_for_deprecation"


def test_generate_warnings_no_warnings():
    """Test _generate_warnings with no issues."""
    warnings = _generate_warnings(
        is_log_extracted=True,
        is_runtime_analysis_enabled=True
    )

    assert warnings == []
    assert len(warnings) == 0


def test_generate_warnings_log_not_extracted():
    """Test _generate_warnings when log extraction fails."""
    warnings = _generate_warnings(
        is_log_extracted=False,
        is_runtime_analysis_enabled=True
    )

    assert len(warnings) == 1
    assert warnings[0] == "Problems while extracting logs: Skipping log analysis"


def test_generate_warnings_runtime_not_enabled():
    """Test _generate_warnings when runtime analysis is not enabled."""
    warnings = _generate_warnings(
        is_log_extracted=True,
        is_runtime_analysis_enabled=False
    )

    assert len(warnings) == 1
    assert warnings[0] == "Problems while connecting to log extractor: Skipping log analysis"


def test_generate_warnings_both_issues():
    """Test _generate_warnings when both log extraction and runtime analysis fail."""
    warnings = _generate_warnings(
        is_log_extracted=False,
        is_runtime_analysis_enabled=False
    )

    assert len(warnings) == 2
    assert "Problems while extracting logs: Skipping log analysis" in warnings
    assert "Problems while connecting to log extractor: Skipping log analysis" in warnings
