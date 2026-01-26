import pytest
from pathlib import Path
from unittest.mock import patch

from endpoint_auditor.scanners.usage_scanner import (
    scan_code_usage,
    _find_client_files_in_project,
    _search_endpoint_in_file
)
from endpoint_auditor.models import CodeUsage


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "clients"

# ==========================================
# Tests for scan_code_usage() - Full Integration
# ==========================================


def test_find_client_files_in_fixtures_directory():
    """Test finding Client files in fixtures directory."""
    client_files = _find_client_files_in_project(str(FIXTURES_DIR))

    assert len(client_files) == 4
    filenames = [f.name for f in client_files]
    assert "UserClient.java" in filenames
    assert "PaymentClient.java" in filenames
    assert "OrderClient.java" in filenames
    assert "ApiClient.java" in filenames
    assert "NotAService.java" not in filenames

def test_find_client_files_in_nonexistent_directory():
    """Test finding files in a non-existent directory raises ValueError."""
    with pytest.raises(ValueError, match="project path not found"):
        _find_client_files_in_project("/nonexistent/path")

def test_search_endpoint_in_user_client():
    """Test searching for /api/v1/users in UserClient.java."""
    user_client = FIXTURES_DIR / "UserClient.java"

    matches = _search_endpoint_in_file(user_client, "/api/v1/users")

    # Exact count: 6 occurrences in the file
    assert matches == 6

def test_search_endpoint_in_payment_client():
    """Test searching for /api/v1/payment in PaymentClient.java."""
    payment_client = FIXTURES_DIR / "PaymentClient.java"

    matches = _search_endpoint_in_file(payment_client, "/api/v1/payment")

    # Exact count: 6 occurrences in the file
    assert matches == 6

def test_search_endpoint_no_matches():
    """Test searching for non-existent endpoint."""
    user_client = FIXTURES_DIR / "UserClient.java"

    matches = _search_endpoint_in_file(user_client, "/api/v9/nonexistent")

    assert matches == 0

def test_search_endpoint_file_not_readable():
    """Test searching in a non-readable file raises ValueError."""
    with pytest.raises(ValueError, match="cannot be open"):
        _search_endpoint_in_file(Path("/nonexistent/file.java"), "/api/v1/test")

def test_scan_code_usage_finds_users_endpoint():
    """Test scanning fixtures for /api/v1/users endpoint."""
    result = scan_code_usage("/api/v1/users", [str(FIXTURES_DIR)])

    assert isinstance(result, CodeUsage)
    assert result.projects_paths == [str(FIXTURES_DIR)]
    assert result.matches_count == 7  # 6 in UserClient + 1 in nested ApiClient
    assert len(result.files) == 2

    # Check that UserClient.java is in results
    assert any("UserClient.java" in f for f in result.files)
    assert any("ApiClient.java" in f for f in result.files)

def test_scan_code_usage_finds_payment_endpoint():
    """Test scanning fixtures for /api/v1/payment endpoint."""
    result = scan_code_usage("/api/v1/payment", [str(FIXTURES_DIR)])

    assert result.matches_count == 6  # 6 occurrences in PaymentClient
    assert len(result.files) == 1
    assert "PaymentClient.java" in result.files[0]

def test_scan_code_usage_no_matches():
    """Test scanning for non-existent endpoint."""
    result = scan_code_usage("/api/v99/nonexistent", [str(FIXTURES_DIR)])

    assert result.matches_count == 0
    assert result.files == []

def test_scan_code_usage_nonexistent_project_path():
    """Test scanning with non-existent project path raises ValueError."""
    with pytest.raises(ValueError, match="project path not found"):
        scan_code_usage("/api/v1/test", ["/nonexistent/path"])

@patch('endpoint_auditor.scanners.usage_scanner._search_endpoint_in_file')
def test_scan_code_usage_handles_file_errors(mock_search):
    """Test that scan continues even if some files raise errors."""
    # Mock to raise error for one file, return count for others
    def side_effect(file_path, endpoint):
        if "UserClient.java" in str(file_path):
            raise ValueError("cannot be open: test error")
        return 0  # No matches for other files

    mock_search.side_effect = side_effect

    # Should not raise exception, just print error and continue
    result = scan_code_usage("/api/v1/test", [str(FIXTURES_DIR)])

    # Should complete successfully
    assert isinstance(result, CodeUsage)
    assert result.matches_count == 0
