from typing import Any, Dict, List
from dataclasses import asdict
from datetime import datetime, timezone

from endpoint_auditor.models import LogExtraction, RuntimeUsage, CodeUsage, Recommendation


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _generate_warnings(
    is_log_extracted: bool,
    is_runtime_analysis_enabled: bool
) -> List[str]:
    """
    Generate a list of warnings based on if the log analysis went fine or not.
    """

    warnings: List[str] = []
    if not is_log_extracted:
        warnings.append("Problems while extracting logs: Skipping log analysis")
    if not is_runtime_analysis_enabled:
        warnings.append("Problems while connecting to log extractor: Skipping log analysis")
    return warnings


def generate_base_report(
    log_extracted: LogExtraction,
    runtime_usage: RuntimeUsage,
    code_usage: CodeUsage
) -> Dict[str, Any]:
    """
    Generate the base report that then is managed to be converted to some specific format
    or reported to an external platform (ex. Jira).
    """

    if runtime_usage.enabled and (runtime_usage.total_occurrences or 0) > 0:
        recommendation = Recommendation(
            status="runtime_usage_detected",
            rationale="Runtime log occurrences were detected in the specified time range.",
        )
    elif code_usage.matches_count > 0:
        recommendation = Recommendation(
            status="still_referenced_in_code",
            rationale="Static references to the endpoint were found in the scanned codebases.",
        )
    else:
        recommendation = Recommendation(
            status="candidate_for_deprecation",
            rationale="No runtime usage detected and no static references found in scanned codebases.",
        )

    return {
        "metadata": {
            "generated_at": _utc_now_iso(),
            "version": "0.1.0",
        },
        "log_extraction": asdict(log_extracted),
        "runtime_usage": asdict(runtime_usage),
        "code_usage": asdict(code_usage),
        "recommendation": asdict(recommendation),
        "warnings": _generate_warnings(log_extracted.extracted, runtime_usage.enabled),
    }
