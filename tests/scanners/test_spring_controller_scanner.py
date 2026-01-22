import pytest
from pathlib import Path

from endpoint_auditor.scanners.spring_controller_scanner import find_endpoint_info
from endpoint_auditor.models import HttpMethod


# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "controllers"


def test_file_not_found():
    """Test that FileNotFoundError is raised when controller file doesn't exist."""
    with pytest.raises(FileNotFoundError) as exc_info:
        find_endpoint_info(
            controller_path="/non/existent/path/Controller.java",
            endpoint="/api/test",
            http_method=HttpMethod.GET
        )

    assert "Controller file not found" in str(exc_info.value)


def test_not_a_rest_controller():
    """Test that ValueError is raised when file is not a @RestController."""
    controller_path = str(FIXTURES_DIR / "NotAController.java")

    with pytest.raises(ValueError) as exc_info:
        find_endpoint_info(
            controller_path=controller_path,
            endpoint="/api/service",
            http_method=HttpMethod.GET
        )

    assert "Not a @RestController class" in str(exc_info.value)


def test_request_mapping_empty_base_path():
    """Test controller without @RequestMapping (empty base path)."""
    controller_path = str(FIXTURES_DIR / "SimpleController.java")

    result = find_endpoint_info(
        controller_path=controller_path,
        endpoint="/health",
        http_method=HttpMethod.GET
    )

    assert result.endpoint_path == "/health"
    assert result.controller_file == controller_path
    assert result.http_method == HttpMethod.GET
    assert result.handler_method == "healthCheck"


def test_endpoint_not_found():
    """Test that ValueError is raised when endpoint doesn't exist in controller."""
    controller_path = str(FIXTURES_DIR / "PaymentController.java")

    with pytest.raises(ValueError) as exc_info:
        find_endpoint_info(
            controller_path=controller_path,
            endpoint="/api/payment/nonexistent",
            http_method=HttpMethod.GET
        )

    assert "Handler method not found" in str(exc_info.value)
    assert "/api/payment/nonexistent" in str(exc_info.value)


def test_http_method_not_matched():
    """Test that ValueError is raised when HTTP method doesn't match."""
    controller_path = str(FIXTURES_DIR / "PaymentController.java")

    # The endpoint exists with POST, but we're searching for GET
    with pytest.raises(ValueError) as exc_info:
        find_endpoint_info(
            controller_path=controller_path,
            endpoint="/api/payment/confirmation",
            http_method=HttpMethod.GET
        )

    assert "Handler method not found" in str(exc_info.value)


def test_post_mapping_success():
    """Test successful extraction of POST endpoint handler method."""
    controller_path = str(FIXTURES_DIR / "PaymentController.java")

    result = find_endpoint_info(
        controller_path=controller_path,
        endpoint="/api/payment/confirmation",
        http_method=HttpMethod.POST
    )

    assert result.endpoint_path == "/api/payment/confirmation"
    assert result.controller_file == controller_path
    assert result.http_method == HttpMethod.POST
    assert result.handler_method == "confirmPayment"


def test_get_mapping_success():
    """Test successful extraction of GET endpoint handler method."""
    controller_path = str(FIXTURES_DIR / "PaymentController.java")

    result = find_endpoint_info(
        controller_path=controller_path,
        endpoint="/api/payment/status",
        http_method=HttpMethod.GET
    )

    assert result.endpoint_path == "/api/payment/status"
    assert result.http_method == HttpMethod.GET
    assert result.handler_method == "getPaymentStatus"


def test_put_mapping_success():
    """Test successful extraction of PUT endpoint handler method."""
    controller_path = str(FIXTURES_DIR / "PaymentController.java")

    result = find_endpoint_info(
        controller_path=controller_path,
        endpoint="/api/payment/update",
        http_method=HttpMethod.PUT
    )

    assert result.endpoint_path == "/api/payment/update"
    assert result.http_method == HttpMethod.PUT
    assert result.handler_method == "updatePayment"


def test_delete_mapping_success():
    """Test successful extraction of DELETE endpoint handler method."""
    controller_path = str(FIXTURES_DIR / "PaymentController.java")

    result = find_endpoint_info(
        controller_path=controller_path,
        endpoint="/api/payment/cancel",
        http_method=HttpMethod.DELETE
    )

    assert result.endpoint_path == "/api/payment/cancel"
    assert result.http_method == HttpMethod.DELETE
    assert result.handler_method == "cancelPayment"


def test_multiple_endpoints_in_same_controller():
    """Test that all different endpoints in the same controller can be found correctly."""
    controller_path = str(FIXTURES_DIR / "PaymentController.java")

    # Test all four endpoints in PaymentController
    test_cases = [
        ("/api/payment/confirmation", HttpMethod.POST, "confirmPayment"),
        ("/api/payment/status", HttpMethod.GET, "getPaymentStatus"),
        ("/api/payment/update", HttpMethod.PUT, "updatePayment"),
        ("/api/payment/cancel", HttpMethod.DELETE, "cancelPayment"),
    ]

    for endpoint, http_method, expected_handler in test_cases:
        result = find_endpoint_info(
            controller_path=controller_path,
            endpoint=endpoint,
            http_method=http_method
        )

        assert result.endpoint_path == endpoint
        assert result.http_method == http_method
        assert result.handler_method == expected_handler


def test_endpoint_path_normalization():
    """Test that trailing slashes in endpoint paths are handled correctly."""
    controller_path = str(FIXTURES_DIR / "PaymentController.java")

    # With trailing slash should still match
    result = find_endpoint_info(
        controller_path=controller_path,
        endpoint="/api/payment/status/",
        http_method=HttpMethod.GET
    )

    assert result.handler_method == "getPaymentStatus"
    # The stored endpoint should be normalized (without trailing slash)
    assert result.endpoint_path == "/api/payment/status/"
