from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class HttpMethod(str, Enum):
    """HTTP methods enum that inherits from str for compatibility with Python 3.9+"""
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"

    @classmethod
    def from_str(cls, value: str) -> "HttpMethod":
        """
        Convert a string to HttpMethod (case-insensitive).

        Valid examples:
        - "get", "GET", "Get"
        - " post "
        """
        try:
            return cls(value.strip().upper())
        except ValueError as e:
            raise ValueError(f"Invalid HTTP method: {value}") from e


@dataclass(frozen=True)
class EndpointInfo:
    """
    Contains all information about an endpoint

    :var endpoint_path: Url related to the endpoint
    :var controller_file: Path to the rest controller
    :var http_method: HTTP method of the endpoint
    :var handler_method: Method that handles this endoint response
    """
    endpoint_path: str
    controller_file: str
    http_method: HttpMethod
    handler_method: Optional[str]


@dataclass(frozen=True)
class LogExtraction:
    """
    Contains all information related with the extraction of a log

    :var log_template: Template extracted from the log
    :var extracted: True if it was succesfully extracted, false otherwise
    """
    log_template: Optional[str]
    extracted: bool


@dataclass(frozen=True)
class RuntimeUsage:
    """
    Contains all information related with the run time analysis usage

    :var enabled: If was performed
    :var provider: The name of the log provider
    :var days: Amount of days in which search the log
    :var total_occurrences: Totale occurences of the log in the last n days
    :var skipped_reason: Description
    """
    enabled: bool
    provider: Optional[str]
    days: int
    total_occurrences: Optional[int]


@dataclass(frozen=True)
class CodeUsage:
    """
    Contains all information related with the analysis of the code usage

    :var projects_paths: List of projects in which search
    :var matches_count: Count of matches
    :var files: Name of the files in which the match was found
    """
    projects_paths: List[str]
    matches_count: int
    files: List[str]


@dataclass(frozen=True)
class Recommendation:
    """
    Final recommendation about the endpoint deprecation

    :var status: Status for the deprecation
    :var rationale: Motivation related with the status
    """
    status: str  # "candidate_for_deprecation" | "still_referenced_in_code" | "runtime_usage_detected"
    rationale: str
