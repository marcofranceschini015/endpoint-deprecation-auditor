import re
from pathlib import Path
from typing import Optional

from endpoint_auditor.models import EndpointInfo, HttpMethod

# Pattern constants
REQUEST_MAPPING_PATTERN = r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']\s*\)'
REST_CONTROLLER_PATTERN = r'@RestController'
# Pattern to match method annotations - more flexible to handle various Java formatting
# Matches: @PostMapping("/path") or @PostMapping
# Followed by method signature (with generics, modifiers, etc.)
HTTP_MAPPING_PATTERN = r'@{annotation}\s*(?:\(\s*(?:value\s*=\s*)?["\']([^"\']*?)["\']\s*\))?\s+(?:[\w<>,\s]+\s+)?(\w+)\s*\('


def find_endpoint_info(
    controller_path: str,
    endpoint: str,
    http_method: HttpMethod
) -> EndpointInfo:
    """
    Find endpoint handler method in a Spring REST controller.

    Args:
        controller_path: Absolute path to the Java REST controller file
        endpoint: The endpoint URL (e.g., "/api/payment/confirmation")
        http_method: The HTTP method (GET, POST, etc.)

    Returns:
        EndpointInfo with the handler method name

    Raises:
        FileNotFoundError: If controller file doesn't exist
        ValueError: If endpoint not found in controller
    """
    controller_file = Path(controller_path)
    if not controller_file.exists():
        raise FileNotFoundError(f"Controller file not found: {controller_path}")
    content = controller_file.read_text(encoding='utf-8')

    base_path = _extract_base_path(content)
    handler_method = _find_handler_method(content, endpoint, http_method, base_path)

    if not handler_method:
        raise ValueError(
            f"Handler method not found for endpoint '{endpoint}' "
            f"with HTTP method '{http_method}' in {controller_path}"
        )

    return EndpointInfo(
        endpoint_path=endpoint,
        controller_file=controller_path,
        http_method=http_method,
        handler_method=handler_method
    )


def _extract_base_path(content: str) -> str:
    """
    Extract the base path from @RequestMapping annotation at class level.

    Returns empty string if no @RequestMapping found.
    """
    if not re.search(REST_CONTROLLER_PATTERN, content):
        raise ValueError("Not a @RestController class")

    request_mapping = re.search(REQUEST_MAPPING_PATTERN, content)

    if not request_mapping:
        return ""

    base_path = request_mapping.group(1).rstrip('/')
    return base_path


def _find_handler_method(
    content: str,
    endpoint: str,
    http_method: HttpMethod,
    base_path: str
) -> Optional[str]:
    """
    Find the handler method name that matches the endpoint and HTTP method.
    """
    endpoint = endpoint.rstrip('/')

    annotation_map = {
        HttpMethod.GET: "GetMapping",
        HttpMethod.POST: "PostMapping",
        HttpMethod.PUT: "PutMapping",
        HttpMethod.DELETE: "DeleteMapping",
        HttpMethod.PATCH: "PatchMapping",
    }

    spring_annotation = annotation_map.get(http_method)
    if not spring_annotation:
        raise ValueError(f"Http method not supported: {http_method}")

    pattern = HTTP_MAPPING_PATTERN.format(annotation=spring_annotation)

    for match in re.finditer(pattern, content, re.MULTILINE):
        method_path = match.group(1) if match.group(1) else ""
        method_name = match.group(2)

        full_path = _build_full_path(base_path, method_path)

        if full_path == endpoint:
            return method_name

    return None


def _build_full_path(base_path: str, method_path: str) -> str:
    """
    Combine base path and method path into full endpoint path.
    """
    base = base_path.rstrip('/')
    method = method_path.strip().rstrip('/')

    if not method:
        return base if base else "/"

    if method.startswith('/'):
        if base:
            return f"{base}{method}"
        return method
    else:
        if base:
            return f"{base}/{method}"
        return f"/{method}"

