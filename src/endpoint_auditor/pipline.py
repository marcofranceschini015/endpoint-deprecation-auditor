from __future__ import annotations

from typing import Any, Dict, List

from endpoint_auditor.scanners.log_extractor import extract_log
from endpoint_auditor.scanners.spring_controller_scanner import find_endpoint_info
from endpoint_auditor.scanners.usage_scanner import scan_code_usage
from endpoint_auditor.reporters.base_reporter import generate_base_report
from endpoint_auditor.models import EndpointInfo, LogExtraction, RuntimeUsage, CodeUsage

from endpoint_auditor.integrations.graylog_mcp import count_log_occurrences

def run_pipeline(
    endpoint: str,
    controller_path: str,
    projects_paths: List[str],
    days: int,
) -> Dict[str, Any]:
    """
    Orchestrates the endpoint deprecation audit.

    The pipeline always performs static analysis. Runtime analysis (Graylog) is executed only if enabled.
    Returns a JSON-serializable report dictionary.
    """
    endpoint_info: EndpointInfo = find_endpoint_info(controller_path=controller_path, endpoint=endpoint)

    log_extracted: LogExtraction = extract_log(controller_path=controller_path, handler_method=endpoint_info.handler_method)

    runtime_usage: RuntimeUsage = count_log_occurrences(log_extracted=log_extracted, days=days)

    code_usage: CodeUsage = scan_code_usage(endpoint=endpoint, projects_paths=projects_paths)

    return generate_base_report(
        endpoint_info=endpoint_info,
        log_extracted=log_extracted,
        runtime_usage=runtime_usage,
        code_usage=code_usage
    )
