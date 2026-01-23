from endpoint_auditor.models import LogExtraction, RuntimeUsage
from endpoint_auditor.integrations.graylog_mcp_client import GraylogMCPClient
from endpoint_auditor.config import is_graylog_enabled


async def count_log_occurrences(
    log_extracted: LogExtraction,
    days: int,
    application_name: str
) -> RuntimeUsage:
    """
    Count log occurrences for a given endpoint in Graylog.

    Args:
        log_extracted: The log extraction data containing endpoint and query
        days: Number of days to search
        application_name: Name of the Graylog stream

    Returns:
        RuntimeUsage with the count of occurrences
    """

    if not is_graylog_enabled() or not log_extracted.extracted or not log_extracted.log_template:
        return _create_default_runtime_usage(days=days)

    try:
        client = GraylogMCPClient()
        count = await client.get_log_count_by_stream_name(
            stream_name=application_name,
            query=_build_query(log_extracted.log_template),
            days=days
        )

        return RuntimeUsage(
            enabled=True,
            provider="Graylog",
            days=days,
            total_occurrences=count
        )
    except Exception:
        return _create_default_runtime_usage(days=days)


def _create_default_runtime_usage(days: int) -> RuntimeUsage:
    return RuntimeUsage(
        enabled=False,
        provider=None,
        days=days,
        total_occurrences=None
    )


def _build_query(log_template: list[str]) -> str:
    """
    Build a Lucene query from log template strings.

    Args:
        log_template: List of log template strings

    Returns:
        Lucene query with strings wrapped in quotes and joined with AND
        Example: '"Downloading Acceptance Document" AND "for case:"'
    """
    if not log_template:
        return ""

    quoted_strings = [f'"{template}"' for template in log_template]
    return " AND ".join(quoted_strings)
