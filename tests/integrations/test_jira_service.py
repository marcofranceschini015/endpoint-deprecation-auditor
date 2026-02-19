import pytest
from unittest.mock import patch, MagicMock

from endpoint_auditor.integrations.jira_service import (
    post_report_to_jira,
    format_report,
)


def _build_report(
    status="candidate_for_deprecation",
    rationale="No runtime usage detected and no static references found.",
    runtime_enabled=True,
    provider="Graylog",
    days=30,
    total_occurrences=0,
    matches_count=0,
    files=None,
    projects_paths=None,
    log_extracted=True,
    log_template=None,
    warnings=None,
):
    """Helper to build a report dict matching generate_base_report() output."""
    return {
        "metadata": {
            "generated_at": "2026-02-19T10:00:00+00:00",
            "version": "0.1.0",
        },
        "log_extraction": {
            "log_template": log_template or ["Downloading document", "for case:"],
            "extracted": log_extracted,
        },
        "runtime_usage": {
            "enabled": runtime_enabled,
            "provider": provider,
            "days": days,
            "total_occurrences": total_occurrences,
        },
        "code_usage": {
            "projects_paths": projects_paths or ["/app/projects/svc-a"],
            "matches_count": matches_count,
            "files": files or [],
        },
        "recommendation": {
            "status": status,
            "rationale": rationale,
        },
        "warnings": warnings or [],
    }


class TestFormatReport:
    """Tests for the report formatting logic."""

    def test_candidate_for_deprecation(self):
        report = _build_report()
        result = format_report(report)

        assert "Endpoint Deprecation Audit Report" in result
        assert "Candidate for Deprecation" in result
        assert "(/)" in result

    def test_runtime_usage_detected(self):
        report = _build_report(
            status="runtime_usage_detected",
            rationale="Runtime log occurrences were detected.",
            total_occurrences=42,
        )
        result = format_report(report)

        assert "(x)" in result
        assert "Runtime Usage Detected" in result
        assert "42" in result
        assert "Graylog" in result

    def test_still_referenced_in_code(self):
        report = _build_report(
            status="still_referenced_in_code",
            rationale="Static references found.",
            matches_count=3,
            files=["ClientA.java", "ClientB.java", "ClientC.java"],
        )
        result = format_report(report)

        assert "(warning)" in result
        assert "Still Referenced in Code" in result
        assert "3" in result
        assert "ClientA.java" in result
        assert "ClientB.java" in result
        assert "ClientC.java" in result

    def test_runtime_not_enabled(self):
        report = _build_report(runtime_enabled=False, provider=None)
        result = format_report(report)

        assert "not performed" in result

    def test_log_extraction_failed(self):
        report = _build_report(log_extracted=False)
        result = format_report(report)

        assert "extraction failed" in result

    def test_warnings_included(self):
        report = _build_report(
            warnings=["Problems while extracting logs: Skipping log analysis"]
        )
        result = format_report(report)

        assert "Warnings" in result
        assert "Problems while extracting logs" in result

    def test_no_warnings_section_when_empty(self):
        report = _build_report(warnings=[])
        result = format_report(report)

        assert "h3. Warnings" not in result

    def test_metadata_footer(self):
        report = _build_report()
        result = format_report(report)

        assert "2026-02-19T10:00:00+00:00" in result
        assert "v0.1.0" in result

    def test_log_template_displayed(self):
        report = _build_report(
            log_template=["Downloading document", "for case:"]
        )
        result = format_report(report)

        assert "Downloading document" in result
        assert "for case:" in result

    def test_multiple_projects_scanned(self):
        report = _build_report(
            projects_paths=["/app/projects/svc-a", "/app/projects/svc-b"]
        )
        result = format_report(report)

        assert "2" in result


class TestPostReportToJira:
    """Tests for the post_report_to_jira orchestration."""

    @patch('endpoint_auditor.integrations.jira_service.is_jira_enabled')
    def test_jira_not_enabled_raises(self, mock_is_enabled):
        mock_is_enabled.return_value = False

        with pytest.raises(RuntimeError, match="not enabled"):
            post_report_to_jira("PROJ-123", _build_report())

    @patch('endpoint_auditor.integrations.jira_service.is_jira_enabled')
    @patch('endpoint_auditor.integrations.jira_service.JiraClient')
    def test_post_report_success(self, mock_client_class, mock_is_enabled):
        mock_is_enabled.return_value = True

        mock_client = MagicMock()
        mock_client.add_comment.return_value = {"id": "12345"}
        mock_client_class.return_value = mock_client

        post_report_to_jira("PROJ-123", _build_report())

        mock_client.add_comment.assert_called_once()
        call_kwargs = mock_client.add_comment.call_args
        assert call_kwargs.kwargs["issue_key"] == "PROJ-123"
        assert "Endpoint Deprecation Audit Report" in call_kwargs.kwargs["comment"]

    @patch('endpoint_auditor.integrations.jira_service.is_jira_enabled')
    @patch('endpoint_auditor.integrations.jira_service.JiraClient')
    def test_post_report_propagates_client_error(self, mock_client_class, mock_is_enabled):
        mock_is_enabled.return_value = True

        mock_client = MagicMock()
        mock_client.add_comment.side_effect = Exception("Jira unavailable")
        mock_client_class.return_value = mock_client

        with pytest.raises(Exception, match="Jira unavailable"):
            post_report_to_jira("PROJ-123", _build_report())
