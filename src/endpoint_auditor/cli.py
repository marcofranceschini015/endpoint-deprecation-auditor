import click

from config import settings, is_graylog_enabled, is_jira_enabled
from endpoint_auditor.pipline import run_pipeline
from reporters import md_reporter, json_reporter, pdf_reporter


@click.command()
@click.option(
    "--endpoint",
    required=True,
    help="The full path of the endpoint (e.g. '/v1/users/verify')",
)
@click.option(
    "--controller-path",
    required=True,
    help="Path to the controller file containing the endpoint handler",
)
@click.option(
    "--days",
    default=30,
    help="Number of days to look back for runtime usage in Graylog",
)
@click.option(
    "--out-dir",
    default="./reports",
    help="Directory to save the generated reports",
)
@click.option(
    "--jira",
    default=None,
    help="Jira ticket ID (optional) to post the report",
)
def audit(
    endpoint, controller_path, days, out_dir, jira
):
    """
    Audit a given endpoint to determine whether it can be deprecated.
    """
    print(f"Running deprecation audit for endpoint: {endpoint}")

    # Get the projects paths from the environment
    projects_paths = settings.default_projects_paths.split(",")

    # Start pipeline execution
    result = run_pipeline(
        endpoint,
        controller_path,
        projects_paths,
        days,
    )

    # Report generation
    if is_jira_enabled() and jira:
        # Attach to Jira ticket
        print(f"Posting report to Jira ticket: {jira}")
        # You would call the Jira MCP tool here (mcp-atlassian)
        pass
    else:
        # Generate reports locally
        json_reporter.generate(result, out_dir)
        md_reporter.generate(result, out_dir)
        if is_graylog_enabled():
            pdf_reporter.generate(result, out_dir)

    print("Audit complete.")
    print(f"Reports saved in: {out_dir}")


if __name__ == "__main__":
    # Ensure the command is run in a valid environment
    if not is_graylog_enabled() and not is_jira_enabled():
        print("Error: No valid integrations configured. Skipping audit.")
        exit(1)

    # Run the CLI command
    audit()
