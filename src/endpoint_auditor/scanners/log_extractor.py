import re
from typing import List

from endpoint_auditor.models import LogExtraction

# Pattern constants
PLACEHOLDER_SLF4J = r'\{\}'
PLACEHOLDER_STRING_FORMAT = r'%\d*\$?[sdioxXeEfgGaAcbBhHntp]'
PLACEHOLDER_MARKER = '|||PLACEHOLDER|||'


def extract_log(log: str) -> LogExtraction:
    """
    Extract log template from a log string.

    Extracts only the constant part of the log message, removing placeholders.

    Args:
        log: The log string to extract template from

    Returns:
        LogExtraction with the log template (constant part only) and extraction status.
        extracted=False only when the log string is empty.
    """
    if not log or not log.strip():
        return LogExtraction(log_template=None, extracted=False)

    constant_parts = _extract_constant_parts(log)
    return LogExtraction(log_template=constant_parts, extracted=True)


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
