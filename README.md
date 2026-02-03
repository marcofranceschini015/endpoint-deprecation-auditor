# Endpoint Deprecation Auditor

CLI tool to assess whether a API endpoint can be safely deprecated by correlating codebase usage and runtime log occurrence analysis.

---

## Motivation

Deprecating an API endpoint safely requires answering two key questions:

- Is the endpoint still referenced anywhere in the codebase?
- Has it been called recently in production?

This tool automates the **endpoint deprecation assessment** by combining:

- Static analysis across multiple projects
- Runtime analysis via log aggregation tools (currently Graylog)

The goal is to provide objective evidence to confidently mark an endpoint as deprecated and remove its related code.

---

## Features

- Spring REST controller analysis to locate the endpoint handler
- Extraction of a representative log template (e.g. `"message {}"`)
- Runtime usage analysis via **Graylog** (occurrence count over last _N_ days)
- Multi-project codebase scan for endpoint path usage
- Report generation:
  - JSON
  - Markdown
  - PDF
- Optional Jira ticket update with assessment results

---

## High-Level Workflow

1. Provide an **endpoint path** (path-only, e.g. `/v1/users/verify`)
2. Locate the corresponding Spring controller method
3. Extract a representative log message template
4. Query Graylog for log occurrences in the last _X_ days
5. Scan specified project directories for endpoint usage
6. Generate a deprecation assessment report or attach it to a Jira ticket

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
DEFAULT_PROJECTS_PATHS=service-a,service-b,frontend
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

**Note:** Both `--controller-path` and `DEFAULT_PROJECTS_PATHS` should be relative to the `/app/projects` folder inside the container.

Run the command (Without JIRA integration)
```bash
docker compose run --rm endpoint-auditor \
  python -m endpoint_auditor.cli \
  --endpoint "/v1/users/verify" \
  --http-method "GET" \
  --controller-path "service-a/src/main/java/.../UserController.java" \
  --application-name "service-a" \
  --days 30 \
  --out-dir "/app/reports"
```

Run the command (With JIRA integration)
```bash
docker compose run --rm endpoint-auditor \
  python -m endpoint_auditor.cli \
  --endpoint "/v1/users/verify" \
  --http-method "GET" \
  --controller-path "service-a/src/main/java/.../UserController.java" \
  --application-name "service-a" \
  --days 30 \
  --out-dir "/app/reports" \
  --jira "TICKET-1234"
```

## Notes:
- `PROJECTS_ROOT_PATH` defines the host directory mounted as `/app/projects` in the container
- `DEFAULT_PROJECTS_PATHS` should contain paths relative to `/app/projects`
- `--controller-path` should be relative to `/app/projects`
- Reports written under `/app/reports` will be visible on your host via the volume mount

---

## Report Contents

Each generated report contains the following information:

### Endpoint Information
- Endpoint path
- Controller file path
- Handler method name

### Log Extraction
- Extracted log template (e.g. `"calling endpoint {}"`)
- Fallback strategy used (if no log template is found)

### Runtime Usage (Graylog)
- Time range analyzed (last _N_ days)
- Query used for log search
- Total number of occurrences

### Code Usage Analysis
- Number of matches found
- List of files referencing the endpoint path

### Automated Recommendation
Based on collected evidence, the tool provides a recommendation:
- **Candidate for deprecation** (no runtime usage, no code references)
- **Still referenced in code**
- **Runtime usage detected**

### Warnings
- Missing log templates
- Fallback strategies applied
- Partial or inconclusive analysis

---

## Configuration

All configuration is managed through environment variables (`.env`):

```env
# Jira
JIRA_BASE_URL=https://jira.example.com
JIRA_EMAIL=your.email@company.com
JIRA_TOKEN=your_jira_token

# Graylog
GRAYLOG_BASE_URL=https://graylog.example.com
GRAYLOG_TOKEN=your_graylog_token
GRAYLOG_MCP_BASE_URL=http://localhost:8000/mcp

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
- Queries are executed via an **internal Graylog MCP client** using [fastMCP](https://gofastmcp.com/clients/client)
- Requires `GRAYLOG_BASE_URL`, `GRAYLOG_TOKEN`, and `GRAYLOG_MCP_BASE_URL`
- The MCP client connects directly to the Graylog MCP server
- If configuration is missing, runtime analysis is skipped
- **TODO:** extend support to additional log aggregation tools
  (e.g. Loki, Datadog)

### Jira

- Jira integration uses direct MCP client connection
- Requires `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`
- Reports can be posted directly to Jira tickets with `--jira` flag
- If configuration is missing, Jira update is skipped

---

## Limitations

- Logs emitted only in deeper service layers may not be detected
- Dynamically built endpoints may evade static scanning
- Runtime analysis depends on log retention and indexing policies
- Currently supports **Graylog only**
- External integrations are skipped if configuration is missing

---

## Roadmap

- Support for additional log aggregation tools
- AST-based Spring controller parsing
- OpenAPI / Swagger integration
- CI-friendly “fail if endpoint is still used” mode
- Improved confidence scoring


