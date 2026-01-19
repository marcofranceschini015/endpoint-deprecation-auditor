from endpoint_auditor.models import EndpointInfo

def find_endpoint_info(
    controller_path: str,
    endpoint: str
) -> EndpointInfo:
    return