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
  - Optional PDF
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

## CLI Usage

With Jira integration:

```bash
endpoint-auditor audit \
  --endpoint "/v1/users/verify" \
  --controller-path "/repo/service-a/src/main/java/.../UserController.java" \
  --projects-paths "/repo/service-a,/repo/service-b,/repo/frontend" \
  --days 30 \
  --jira "TICKET-1234"
```

Without Jira (local report output):

```bash
endpoint-auditor audit \
  --endpoint "/v1/users/verify" \
  --controller-path "/repo/service-a/.../UserController.java" \
  --projects-paths "/repo" \
  --days 14 \
  --out-dir "./reports"
```

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

Configuration is split into two parts:

### Environment variables (`.env`)

```env
# Jira
JIRA_BASE_URL=https://jira.example.com
JIRA_EMAIL=your.email@company.com
JIRA_TOKEN=your_jira_token

# Graylog
GRAYLOG_BASE_URL=https://graylog.example.com
GRAYLOG_TOKEN=your_graylog_token

# Default project paths (optional)
DEFAULT_PROJECTS_PATHS=/repo/service-a,/repo/service-b
```
An example configuration file is available in .env.example.

### MCP Configuration(mcp.json)

The project uses an mcp.json file to define external MCP servers
(Jira and Graylog).
Credentials and URLs are resolved from environment variables.
If required variables are missing or invalid, the corresponding
integration is automatically skipped.

---

## Integrations

### Graylog

- Runtime analysis is currently implemented **only for Graylog**
- Integration is defined in `mcp.json`
- Queries are executed via an **internal Graylog MCP tool**
- Requires `GRAYLOG_BASE_URL` and `GRAYLOG_TOKEN`
- If configuration is missing, runtime analysis is skipped
- **TODO:** extend support to additional log aggregation tools
  (e.g. Loki, Datadog)

### Jira

- Jira integration relies on the **`mcp-atlassian` tool**
- Executed via `uvx`
- Configuration is defined in `mcp.json`
- Requires `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`
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


