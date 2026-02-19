# Endpoint Deprecation Auditor

CLI tool to assess whether an API endpoint can be safely deprecated by correlating codebase usage and runtime log occurrence analysis.

---

## Motivation

Deprecating an API endpoint safely requires answering two key questions:

- Is the endpoint still referenced anywhere in the codebase?
- Has it been called recently in production?

This tool automates the **endpoint deprecation assessment** by combining:

- Static analysis across multiple projects (scans `*Client*.java` files for endpoint references)
- Runtime analysis via log aggregation tools (currently Graylog)

The goal is to provide objective evidence to confidently mark an endpoint as deprecated and remove its related code.

---

## Features

- Log template extraction from user-provided log strings (supports SLF4J `{}` and `printf`-style placeholders)
- Runtime usage analysis via **Graylog** (occurrence count over last _N_ days)
- Multi-project codebase scan for endpoint path usage in Java client files
- Automated deprecation recommendation based on collected evidence
- Post assessment report directly to a **Jira** ticket as a formatted comment

---

## High-Level Workflow

1. Provide an **endpoint path** (e.g. `/v1/users/verify`), the **HTTP method**, and a **representative log message**
2. Extract constant parts from the log template (removing placeholders)
3. Query Graylog for log occurrences in the last _N_ days
4. Scan specified project directories for endpoint usage in `*Client*.java` files
5. Generate a deprecation assessment report with an automated recommendation
6. Optionally post the report as a comment on a Jira ticket

---

## Quickstart

### Prerequisites
- Docker + Docker Compose

### Setup
```bash
cp .env.example .env
# edit .env with your values
```

### Project Structure

The tool expects your projects to be organized under a single root directory on your host machine. This directory is mounted into the container at `/app/projects`.

**Important:** Set `PROJECTS_ROOT_PATH` in your `.env` file to point to your local projects root directory:

```env
# Path to your local projects directory (mounted as /app/projects in the container)
PROJECTS_ROOT_PATH=/path/to/your/projects

# Project paths relative to /app/projects
DEFAULT_PROJECTS_PATHS=/app/projects/service-a,/app/projects/service-b,/app/projects/frontend
```

For example, if your projects are structured like this on your host:
```
/Users/me/repos/
├── service-a/
│   └── src/main/java/...
├── service-b/
│   └── src/main/java/...
└── frontend/
    └── src/...
```

Set `PROJECTS_ROOT_PATH=/Users/me/repos` and the paths will be available inside the container under `/app/projects/`.

## Run

Run the audit (without Jira):
```bash
docker compose run --rm endpoint-auditor \
  python -m endpoint_auditor.cli \
  --endpoint "/v1/users/verify" \
  --http-method "GET" \
  --log "Verifying user identity for case: '{}'" \
  --application-name "service-a" \
  --days 30
```

Run the audit and post the report to a Jira ticket:
```bash
docker compose run --rm endpoint-auditor \
  python -m endpoint_auditor.cli \
  --endpoint "/v1/users/verify" \
  --http-method "GET" \
  --log "Verifying user identity for case: '{}'" \
  --application-name "service-a" \
  --days 30 \
  --jira "TICKET-1234"
```

### CLI Options

| Option               | Required | Default | Description                                                     |
|----------------------|----------|---------|-----------------------------------------------------------------|
| `--endpoint`         | Yes      |         | Full path of the endpoint (e.g. `/v1/users/verify`)             |
| `--http-method`      | Yes      |         | HTTP method (`GET`, `POST`, `PUT`, `DELETE`, etc.)              |
| `--log`              | Yes      |         | Representative log emitted when the endpoint is reached. May contain placeholders (e.g. `"Verifying user {}"`) |
| `--application-name` | Yes      |         | Name of the application / Graylog stream emitting the logs      |
| `--days`             | No       | `30`    | Number of days to look back for runtime usage in Graylog        |
| `--jira`             | No       |         | Jira issue key (e.g. `TICKET-1234`) to post the report to       |

### Notes
- `PROJECTS_ROOT_PATH` defines the host directory mounted as `/app/projects` in the container
- `DEFAULT_PROJECTS_PATHS` should contain paths relative to `/app/projects`
- The `--log` argument supports SLF4J placeholders (`{}`) and printf-style placeholders (`%s`, `%d`, etc.)
- If `--jira` is omitted, the report is generated but not posted anywhere

---

## Report Contents

Each generated report contains the following information:

### Log Extraction
- Extracted log template (constant parts only, e.g. `"Verifying user identity for case:"`)
- Extraction status (success/failure)

### Runtime Usage (Graylog)
- Provider name
- Time range analyzed (last _N_ days)
- Total number of occurrences

### Code Usage Analysis
- Projects scanned
- Number of matches found
- List of `*Client*.java` files referencing the endpoint path

### Automated Recommendation
Based on collected evidence, the tool provides a recommendation:
- **Candidate for deprecation** — no runtime usage, no code references
- **Still referenced in code** — static references found in scanned codebases
- **Runtime usage detected** — log occurrences found in the specified time range

### Warnings
- Log template extraction failures
- Runtime analysis skipped (provider not enabled or not reachable)

---

## Configuration

All configuration is managed through environment variables (`.env`):

```env
# Jira
JIRA_BASE_URL=https://jira.example.com
JIRA_EMAIL=your.email@company.com
JIRA_TOKEN=your_jira_api_token

# Graylog
GRAYLOG_MCP_BASE_URL=https://graylog.example.com/mcp/
GRAYLOG_BASE_URL=https://graylog.example.com
GRAYLOG_TOKEN=your_graylog_api_token

# Projects configuration
# Host path to mount as /app/projects in the container
PROJECTS_ROOT_PATH=/path/to/your/projects

# Project paths relative to /app/projects (comma-separated)
DEFAULT_PROJECTS_PATHS=/app/projects/service-a,/app/projects/service-b
```
An example configuration file is available in `.env.example`.

**Note:** If required variables are missing or invalid, the corresponding
integration is automatically skipped.

---

## Integrations

### Graylog

- Runtime analysis is currently implemented **only for Graylog**
- Queries are executed via an **internal Graylog MCP client** using [FastMCP](https://gofastmcp.com/clients/client)
- Requires `GRAYLOG_BASE_URL`, `GRAYLOG_TOKEN`, and `GRAYLOG_MCP_BASE_URL`
- The MCP client connects to the Graylog MCP server via HTTP transport
- If configuration is missing, runtime analysis is skipped

### Jira

- Jira integration uses [atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) to communicate with the Jira REST API
- Requires `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`
- When `--jira` is provided, the report is formatted in Jira wiki markup and posted as a comment on the specified issue
- The comment includes the recommendation, runtime usage table, code usage details, log template, warnings, and metadata
- If configuration is missing, Jira posting is skipped

---

## Limitations

- Logs emitted only in deeper service layers may not be detected
- Dynamically built endpoints may evade static scanning
- Runtime analysis depends on log retention and indexing policies
- Currently supports **Graylog only** for runtime analysis
- Code scan targets `*Client*.java` files only
- External integrations are skipped if configuration is missing

---

## Roadmap

- Support for additional log aggregation tools (e.g. Loki, Datadog)
- AST-based Spring controller parsing
- OpenAPI / Swagger integration
- CI-friendly "fail if endpoint is still used" mode
- Improved confidence scoring
- Local report generation (JSON, Markdown, PDF)
