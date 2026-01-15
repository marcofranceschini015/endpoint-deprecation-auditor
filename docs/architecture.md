# Architecture

## Overview

The **Endpoint Deprecation Auditor** is a CLI-based tool designed to assess
whether an API endpoint can be safely deprecated by correlating:

- **Static analysis** of codebases
- **Runtime analysis** of log occurrences

The architecture follows a **modular and extensible design**, with a clear
separation of responsibilities between orchestration, scanning, integrations
and reporting.

---

## High-Level Architecture

```
CLI
└─ Pipeline
├─ Controller Scanner
│ └─ Log Template Extraction
├─ Runtime Usage Analysis
│ └─ Graylog MCP
├─ Code Usage Scanner
│ └─ ripgrep-based search
└─ Report Generation
├─ JSON
├─ Markdown
└─ PDF (optional)
```

---

## Core Components

### CLI (`cli.py`)
- Parses user input and CLI flags
- Validates required arguments
- Starts the audit pipeline

### Pipeline (`pipeline.py`)
- Orchestrates the full audit workflow
- Handles conditional execution of integrations
- Collects results and warnings
- Produces a unified report model

---

## Scanners

### Spring Controller Scanner
- Locates the handler method matching the provided endpoint path
- Supports common Spring annotations:
  - `@GetMapping`
  - `@PostMapping`
  - `@RequestMapping`
- Extracts contextual information (file, method name)

### Log Template Extractor
- Identifies logging statements inside the handler method
- Extracts the constant part of log messages
  (e.g. `"processing request {}"`)
- Falls back to endpoint-based queries if no log is found

### Code Usage Scanner
- Searches for exact endpoint path usage across multiple directories
- Uses `ripgrep` for fast and reliable scanning
- Collects file paths referencing the endpoint

---

## Integrations

### MCP Loader
- Loads `mcp.json`
- Resolves placeholders using environment variables
- Determines whether integrations are enabled or skipped
- Prevents hard failures caused by missing configuration

### Graylog Integration
- Implemented via an internal Graylog MCP tool
- Performs occurrence-based log queries
- Execution is skipped if configuration is missing

### Jira Integration
- Implemented via `mcp-atlassian` (executed with `uvx`)
- Posts audit results to existing Jira tickets
- Execution is skipped if configuration is missing

---

## Reporting

- A **JSON report** is always generated as the source of truth
- Markdown and PDF reports are derived from the JSON model
- Reports include:
  - Evidence
  - Warnings
  - Automated recommendation

---

## Design Principles

- Single Responsibility per module
- Fail-safe execution (skip, never crash)
- Clear separation between business logic and external systems
- Extensibility for additional log providers and frameworks

---

## Future Extensions

- Support for additional log aggregation tools (Loki, Datadog)
- AST-based parsing for higher controller accuracy
- OpenAPI / Swagger correlation
- CI enforcement and quality gates
