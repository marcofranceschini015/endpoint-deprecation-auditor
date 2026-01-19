from endpoint_auditor.models import LogExtraction

def extract_log(
    controller_path: str,
    handler_method: str    
) -> LogExtraction:
    return