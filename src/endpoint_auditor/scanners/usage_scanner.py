from endpoint_auditor.models import CodeUsage
from typing import List

def scan_code_usage(
    endpoint: str,
    project_paths: List[str]
) -> CodeUsage:
    return