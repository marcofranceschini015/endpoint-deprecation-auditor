from endpoint_auditor.models import LogExtraction, RuntimeUsage

def count_log_occurrences(
    log_extracted: LogExtraction,
    days: int
) -> RuntimeUsage:
    return