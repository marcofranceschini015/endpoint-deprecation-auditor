from __future__ import annotations
from typing import Any, Dict, List

from endpoint_auditor.scanners.log_extractor import extract_log
from endpoint_auditor.scanners.usage_scanner import scan_code_usage
from endpoint_auditor.reporters.base_reporter import generate_base_report
from endpoint_auditor.models import LogExtraction, RuntimeUsage, CodeUsage
from endpoint_auditor.integrations.graylog_service import count_log_occurrences


async def run_pipeline(
    endpoint: str,
    log: str,
    application_name: str,
    projects_paths: List[str],
    days: int,
) -> Dict[str, Any]:
    """
    Orchestrates the endpoint deprecation audit.

    The pipeline always performs static analysis. Runtime analysis (Graylog) is executed only if enabled.
    Returns a JSON-serializable report dictionary.
    """
    log_extracted: LogExtraction = extract_log(log=log)

    runtime_usage: RuntimeUsage = await count_log_occurrences(log_extracted=log_extracted, days=days, application_name=application_name)

    code_usage: CodeUsage = scan_code_usage(endpoint=endpoint, projects_paths=projects_paths)

    return generate_base_report(
        log_extracted=log_extracted,
        runtime_usage=runtime_usage,
        code_usage=code_usage
    )
