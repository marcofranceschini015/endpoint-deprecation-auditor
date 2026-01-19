from dataclasses import dataclass
from typing import Optional
from typing import List


@dataclass(frozen=True)
class EndpointInfo:
    endpoint_path: str
    controller_file: str
    handler_method: Optional[str]


@dataclass(frozen=True)
class LogExtraction:
    log_template: Optional[str]
    extracted: bool


@dataclass(frozen=True)
class RuntimeUsage:
    enabled: bool
    provider: Optional[str]  # "graylog" | None
    days: int
    query: Optional[str]
    total_occurrences: Optional[int]
    skipped_reason: Optional[str]


@dataclass(frozen=True)
class CodeUsage:
    projects_paths: List[str]
    matches_count: int
    files: List[str]


@dataclass(frozen=True)
class Recommendation:
    status: str  # "candidate_for_deprecation" | "still_referenced_in_code" | "runtime_usage_detected"
    rationale: str