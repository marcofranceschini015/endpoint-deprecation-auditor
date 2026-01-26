from endpoint_auditor.models import CodeUsage
from typing import List, Set
from pathlib import Path
import re


def scan_code_usage(
    endpoint: str,
    projects_paths: List[str]
) -> CodeUsage:
    """
    Scan code usage of an endpoint across multiple projects.

    Searches recursively in all project paths for files matching *Client*.java
    and finds exact matches of the endpoint.

    Args:
        endpoint: The endpoint path to search for (e.g., '/api/v1/users')
        projects_paths: List of absolute paths to project directories

    Returns:
        CodeUsage with matches count and list of files containing the endpoint
    """
    matching_files: Set[str] = set()
    total_matches = 0

    all_client_files = _find_client_files(projects=projects_paths)

    for file_path in all_client_files:
        try:
            match_count = _search_endpoint_in_file(file_path, endpoint)
            if match_count > 0:
                matching_files.add(str(file_path))
                total_matches += match_count
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    return CodeUsage(
        projects_paths=projects_paths,
        matches_count=total_matches,
        files=sorted(list(matching_files))
    )


def _find_client_files(projects: List[str]) -> List[Path]:
    """
    Find all Java files containing 'Client' in their name.

    Args:
        projects: List of root directories to search

    Returns:
        List of Path objects for matching files
    """
    all_client_files = []
    for project_path in projects:
        client_files = _find_client_files_in_project(project_path)
        all_client_files.extend(client_files)
    return all_client_files


def _find_client_files_in_project(project_path: str) -> List[Path]:
    """
    Find all Java files containing 'Client' in their name for one specific project.

    Args:
        project_path: Root directory to search

    Returns:
        List of Path objects for matching files
    """
    project_dir = Path(project_path)

    if not project_dir.exists() or not project_dir.is_dir():
        raise ValueError(f"project path not found: {project_path}")

    # Find all .java files recursively that contain 'Client' in the filename
    client_files = []
    for java_file in project_dir.rglob("*.java"):
        if "Client" in java_file.name:
            client_files.append(java_file)

    return client_files


def _search_endpoint_in_file(file_path: Path, endpoint: str) -> int:
    """
    Search for exact endpoint matches in a file.

    Args:
        file_path: Path to the file to search
        endpoint: Endpoint string to search for

    Returns:
        Number of matches found in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Escape special regex characters in endpoint
        escaped_endpoint = re.escape(endpoint)

        # Search for exact matches (as string literal or in URL)
        pattern = re.compile(escaped_endpoint)
        matches = pattern.findall(content)

        return len(matches)
    except Exception as e:
        # If file can't be read, raise exception
        raise ValueError(f"file {file_path} cannot be open: {e}")
