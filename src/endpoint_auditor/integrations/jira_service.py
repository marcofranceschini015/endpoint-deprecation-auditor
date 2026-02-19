from typing import Any, Dict

from endpoint_auditor.config import is_jira_enabled
from endpoint_auditor.integrations.jira_mcp_client import JiraClient


_STATUS_LABELS = {
    "candidate_for_deprecation": "Candidate for Deprecation",
    "still_referenced_in_code": "Still Referenced in Code",
    "runtime_usage_detected": "Runtime Usage Detected",
}

_STATUS_ICONS = {
    "candidate_for_deprecation": "(/)",
    "still_referenced_in_code": "(warning)",
    "runtime_usage_detected": "(x)",
}


def post_report_to_jira(issue_key: str, report: Dict[str, Any]) -> None:
    """
    Format the audit report and post it as a comment on the given Jira issue.

    Args:
        issue_key: Jira issue key (e.g. 'PROJ-123')
        report: Base report dictionary produced by generate_base_report()

    Raises:
        RuntimeError: If Jira is not enabled or posting fails
    """
    if not is_jira_enabled():
        raise RuntimeError("Jira integration is not enabled")

    comment = format_report(report)
    client = JiraClient()
    client.add_comment(issue_key=issue_key, comment=comment)


def format_report(report: Dict[str, Any]) -> str:
    """
    Convert the base report dict into a Markdown comment suitable for Jira.

    Args:
        report: Base report dictionary from generate_base_report()

    Returns:
        Markdown-formatted string
    """
    recommendation = report.get("recommendation", {})
    status = recommendation.get("status", "unknown")
    rationale = recommendation.get("rationale", "")
    icon = _STATUS_ICONS.get(status, "(?)")
    label = _STATUS_LABELS.get(status, status)

    runtime = report.get("runtime_usage", {})
    code = report.get("code_usage", {})
    log_extraction = report.get("log_extraction", {})
    warnings = report.get("warnings", [])
    metadata = report.get("metadata", {})

    sections = [
        f"h2. {icon} Endpoint Deprecation Audit Report",
        "",
        f"*Recommendation:* {icon} *{label}*",
        f"_{rationale}_",
        "",
        _format_runtime_section(runtime),
        _format_code_usage_section(code),
        _format_log_extraction_section(log_extraction),
    ]

    if warnings:
        sections.append(_format_warnings_section(warnings))

    sections.append(_format_metadata_section(metadata))

    return "\n".join(sections)


def _format_runtime_section(runtime: Dict[str, Any]) -> str:
    if not runtime.get("enabled"):
        return (
            "h3. Runtime Usage\n"
            "Runtime analysis was not performed (provider not enabled)."
        )

    provider = runtime.get("provider", "N/A")
    days = runtime.get("days", "N/A")
    occurrences = runtime.get("total_occurrences", 0)

    return (
        "h3. Runtime Usage\n"
        f"||Provider||Time Window||Occurrences||\n"
        f"|{provider}|{days} days|{occurrences}|"
    )


def _format_code_usage_section(code: Dict[str, Any]) -> str:
    matches = code.get("matches_count", 0)
    files = code.get("files", [])
    paths = code.get("projects_paths", [])

    lines = [
        "h3. Code Usage (Static Analysis)",
        f"*Projects scanned:* {len(paths)}",
        f"*Matches found:* {matches}",
    ]

    if files:
        lines.append("*Files with references:*")
        for f in files:
            lines.append(f"* {{{{{f}}}}}")

    return "\n".join(lines)


def _format_log_extraction_section(log_extraction: Dict[str, Any]) -> str:
    extracted = log_extraction.get("extracted", False)
    template = log_extraction.get("log_template")

    if not extracted:
        return (
            "h3. Log Extraction\n"
            "(warning) Log template extraction failed."
        )

    template_str = " ... ".join(template) if template else "N/A"

    return (
        "h3. Log Extraction\n"
        f"*Template:* {{{{{template_str}}}}}"
    )


def _format_warnings_section(warnings: list) -> str:
    lines = ["h3. Warnings"]
    for w in warnings:
        lines.append(f"* (warning) {w}")
    return "\n".join(lines)


def _format_metadata_section(metadata: Dict[str, Any]) -> str:
    generated_at = metadata.get("generated_at", "N/A")
    version = metadata.get("version", "N/A")

    return (
        "\n----\n"
        f"_Generated at {generated_at} | endpoint-deprecation-auditor v{version}_"
    )
