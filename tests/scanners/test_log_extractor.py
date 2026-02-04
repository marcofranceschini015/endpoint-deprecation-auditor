from endpoint_auditor.scanners.log_extractor import extract_log, _extract_constant_parts


# ==========================================
# Tests for extract_log()
# ==========================================

def test_extract_log_empty_string():
    """Test that empty string returns extracted=False."""
    result = extract_log("")

    assert result.extracted is False
    assert result.log_template is None


def test_extract_log_whitespace_only():
    """Test that whitespace-only string returns extracted=False."""
    result = extract_log("   ")

    assert result.extracted is False
    assert result.log_template is None


def test_extract_log_none():
    """Test that None returns extracted=False."""
    result = extract_log(None)

    assert result.extracted is False
    assert result.log_template is None


def test_extract_log_success_with_multiple_placeholders():
    """Test successful extraction with multiple placeholders."""
    log = "Confirming payment. Transaction id: '{}'. Provider: '{}'"

    result = extract_log(log)

    assert result.extracted is True
    assert result.log_template is not None
    assert len(result.log_template) == 3
    assert result.log_template[0] == "Confirming payment. Transaction id: '"
    assert result.log_template[1] == "'. Provider: '"
    assert result.log_template[2] == "'"


def test_extract_log_success_no_placeholders():
    """Test successful extraction with no placeholders."""
    log = "Getting payment status"

    result = extract_log(log)

    assert result.extracted is True
    assert result.log_template is not None
    assert len(result.log_template) == 1
    assert result.log_template[0] == "Getting payment status"


def test_extract_log_success_single_placeholder():
    """Test successful extraction with single placeholder at end."""
    log = "Updating payment for id: {}"

    result = extract_log(log)

    assert result.extracted is True
    assert result.log_template is not None
    assert len(result.log_template) == 1
    assert result.log_template[0] == "Updating payment for id:"


def test_extract_log_only_placeholders():
    """Test extraction when log contains only placeholders."""
    log = "{} {} {}"

    result = extract_log(log)

    assert result.extracted is True
    assert result.log_template is not None
    assert result.log_template == []


# ==========================================
# Tests for _extract_constant_parts() - Unit Tests
# ==========================================

def test_extract_constant_parts_no_placeholders():
    """Test with no placeholders - returns entire string."""
    result = _extract_constant_parts("Hello world")
    assert result == ["Hello world"]


def test_extract_constant_parts_placeholder_at_end():
    """Test with placeholder at end - returns only constant part."""
    result = _extract_constant_parts("Hello {}")
    assert result == ["Hello"]


def test_extract_constant_parts_placeholder_in_middle():
    """Test with placeholder in middle - returns both parts."""
    result = _extract_constant_parts("Hello {} world")
    assert result == ["Hello", "world"]


def test_extract_constant_parts_multiple_placeholders():
    """Test with multiple placeholders - returns all constant parts."""
    result = _extract_constant_parts("Hello {} world {}")
    assert result == ["Hello", "world"]


def test_extract_constant_parts_complex_example():
    """Test with complex real-world example."""
    result = _extract_constant_parts("Downloading Acceptance Document {} for case: {}")
    assert result == ["Downloading Acceptance Document", "for case:"]


def test_extract_constant_parts_string_format():
    """Test with String.format placeholders."""
    result = _extract_constant_parts("User %s logged in at %d")
    assert result == ["User", "logged in at"]


def test_extract_constant_parts_empty_result():
    """Test with only placeholder - returns empty list."""
    result = _extract_constant_parts("{}")
    assert result == []


def test_extract_constant_parts_multiple_consecutive():
    """Test with multiple consecutive placeholders."""
    result = _extract_constant_parts("Start {} {} end")
    assert result == ["Start", "end"]


def test_extract_constant_parts_with_quotes():
    """Test with quotes in constant parts."""
    result = _extract_constant_parts("Transaction: '{}'. Provider: '{}'")
    assert result == ["Transaction: '", "'. Provider: '", "'"]


def test_extract_constant_parts_positional_format():
    """Test with positional format placeholders."""
    result = _extract_constant_parts("Value %1$s and %2$d items")
    assert result == ["Value", "and", "items"]


def test_extract_constant_parts_mixed_placeholders():
    """Test with mixed placeholder types."""
    result = _extract_constant_parts("User {} logged in at %s with code %d")
    assert result == ["User", "logged in at", "with code"]


def test_extract_constant_parts_placeholder_at_start():
    """Test with placeholder at start."""
    result = _extract_constant_parts("{} is the value")
    assert result == ["is the value"]


def test_extract_constant_parts_only_placeholders():
    """Test with only placeholders."""
    result = _extract_constant_parts("{} {} {}")
    assert result == []


def test_extract_constant_parts_whitespace_handling():
    """Test that whitespace is properly stripped."""
    result = _extract_constant_parts("  Start  {}  middle  {}  end  ")
    assert result == ["Start", "middle", "end"]
