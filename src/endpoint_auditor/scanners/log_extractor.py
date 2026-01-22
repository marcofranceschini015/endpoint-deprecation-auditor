import re
from pathlib import Path
from typing import Optional, List

from endpoint_auditor.models import LogExtraction, EndpointInfo

# Pattern constants
LOG_PATTERN_DOUBLE_QUOTES = r'(?:LOGGER|logger|log|LOG)\.(info|debug|warn|error|trace|fatal)\s*\(\s*"([^"]*)"'
LOG_PATTERN_SINGLE_QUOTES = r"(?:LOGGER|logger|log|LOG)\.(info|debug|warn|error|trace|fatal)\s*\(\s*'([^']*)'"
PLACEHOLDER_SLF4J = r'\{\}'
PLACEHOLDER_STRING_FORMAT = r'%\d*\$?[sdioxXeEfgGaAcbBhHntp]'
PLACEHOLDER_MARKER = '|||PLACEHOLDER|||'


def extract_log(
    endpoint_info: EndpointInfo
) -> LogExtraction:
    """
    Extract log statement from the handler method in a Java controller.

    Extracts only the constant part of the log message, removing placeholders.

    Args:
        endpoint_info: Contains controller file path and handler method name

    Returns:
        LogExtraction with the log template (constant part only) and extraction status
    """
    try:
        controller_file = Path(endpoint_info.controller_file)
        if not controller_file.exists():
            raise FileNotFoundError(f"Controller file not found: {endpoint_info.controller_file}")

        content = controller_file.read_text(encoding='utf-8')

        method_body = _extract_method_body(content, endpoint_info.handler_method)
        if not method_body:
            raise ValueError(f"Method body not found for: {endpoint_info.handler_method}")

        log_template = _find_log_statement(method_body)
        if not log_template:
            raise ValueError(f"No log statement found in method: {endpoint_info.handler_method}")

        constant_part = _extract_constant_parts(log_template)

        return LogExtraction(log_template=constant_part, extracted=True)

    except Exception:
        return LogExtraction(log_template=None, extracted=False)


def _extract_method_body(content: str, method_name: str) -> Optional[str]:
    """
    Extract the body of a specific method from Java source code.

    Returns the content between the method's opening and closing braces.
    """
    pattern = rf'\b{re.escape(method_name)}\s*\([^)]*\)\s*\{{'

    match = re.search(pattern, content)
    if not match:
        return None

    start_pos = match.end() - 1
    brace_count = 1
    pos = start_pos + 1

    while pos < len(content) and brace_count > 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1

    if brace_count == 0:
        method_body = content[start_pos + 1:pos - 1]
        return method_body

    return None


def _find_log_statement(method_body: str) -> Optional[str]:
    """
    Find and extract log statement template from method body.

    Supports multiple logging frameworks:
    - Log4j2: LOGGER.info(...)
    - SLF4J: logger.debug(...), log.warn(...)
    - Commons Logging: LOG.error(...)

    Returns the raw log message template (with placeholders).
    """
    matches = re.finditer(LOG_PATTERN_DOUBLE_QUOTES, method_body)
    for match in matches:
        log_template = match.group(2)
        if log_template:
            return log_template

    matches = re.finditer(LOG_PATTERN_SINGLE_QUOTES, method_body)
    for match in matches:
        log_template = match.group(2)
        if log_template:
            return log_template

    return None


def _extract_constant_parts(log_template: str) -> List[str]:
    """
    Extract constant parts from a log template by splitting on placeholders.

    Rules:
    - No placeholders: Return entire template as single element
    - Placeholder at end: Ignore, don't create empty part
    - Placeholder in middle: Split into parts before and after
    - Multiple placeholders: Split into all constant parts, ignore trailing

    Examples:
        "Hello world" → ["Hello world"]
        "Hello {}" → ["Hello"]
        "Hello {} world" → ["Hello", "world"]
        "Hello {} world {}" → ["Hello", "world"]
        "Downloading Document {} for case: {}" → ["Downloading Document", "for case:"]

    Args:
        log_template: The raw log template string with placeholders

    Returns:
        List of constant string parts (non-empty, stripped)
    """
    # Replace all placeholder types with a common marker
    result = re.sub(PLACEHOLDER_SLF4J, PLACEHOLDER_MARKER, log_template)
    result = re.sub(PLACEHOLDER_STRING_FORMAT, PLACEHOLDER_MARKER, result)

    # Split on placeholder marker
    parts = result.split(PLACEHOLDER_MARKER)

    # Filter out empty parts and strip whitespace
    constant_parts = [part.strip() for part in parts if part.strip()]

    # If no constant parts found, return empty list
    if not constant_parts:
        return []

    return constant_parts
