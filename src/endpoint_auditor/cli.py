import asyncio
import click

from config import settings, is_graylog_enabled, is_jira_enabled
from pipline import run_pipeline
from integrations.jira_service import post_report_to_jira


@click.command()
@click.option(
    "--endpoint",
    required=True,
    help="The full path of the endpoint (e.g. '/v1/users/verify')",
)
@click.option(
    "--http-method",
    required=True,
    help="The HTTP method of the endpoint (e.g. 'GET', 'POST', 'PUT', 'DELETE')",
)
@click.option(
    "--log",
    required=True,
    help="One log that appear when the endpoint is reached. Can be also with variables in between," \
    "e.g. \"I am a log {}\""
)
@click.option(
    "--application-name",
    required=True,
    help="Name of the application that is emitting the logs",
)
@click.option(
    "--days",
    default=30,
    help="Number of days to look back for runtime usage in Graylog",
)
@click.option(
    "--jira",
    default=None,
    help="Jira ticket ID (optional) to post the report",
)
def audit(
    endpoint, http_method, log, application_name, days, jira
):
    """
    Audit a given endpoint to determine whether it can be deprecated.
    """
    print(f"Running deprecation audit for endpoint: {endpoint}")

    # Get the projects paths from the environment
    projects_paths = settings.default_projects_paths.split(",")

    # Start pipeline execution
    result = asyncio.run(run_pipeline(
        endpoint=endpoint,
        log=log,
        application_name=application_name,
        projects_paths=projects_paths,
        days=days,
    ))

    if is_jira_enabled() and jira:
        print(f"Posting report to Jira ticket: {jira}")
        post_report_to_jira(issue_key=jira, report=result)
        print(f"Report posted to {jira}")

    print("Audit complete.")


if __name__ == "__main__":
    # Ensure the command is run in a valid environment
    if not is_graylog_enabled() and not is_jira_enabled():
        print("Error: No valid integrations configured. Skipping audit.")
        exit(1)

    # Run the CLI command
    audit()
