"""Test query utilities to verify they work correctly"""
from app.core.query_utils import parse_expand_param


def test_parse_expand_param_single_field():
    """Test parsing a single expand field"""
    result = parse_expand_param("user_account")
    assert result == ["user_account"]
    print("  - Single field: PASS")


def test_parse_expand_param_multiple_fields():
    """Test parsing multiple expand fields"""
    result = parse_expand_param("user_account,service_id,poste_id")
    assert result == ["user_account", "service_id", "poste_id"]
    print("  - Multiple fields: PASS")


def test_parse_expand_param_with_spaces():
    """Test parsing expand fields with spaces"""
    result = parse_expand_param("user_account, service_id , poste_id")
    assert result == ["user_account", "service_id", "poste_id"]
    print("  - Fields with spaces: PASS")


def test_parse_expand_param_empty():
    """Test parsing empty expand parameter"""
    result = parse_expand_param("")
    assert result == []
    print("  - Empty string: PASS")


def test_parse_expand_param_none():
    """Test parsing None expand parameter"""
    result = parse_expand_param(None)
    assert result == []
    print("  - None value: PASS")


def test_parse_expand_param_nested():
    """Test parsing nested expand fields"""
    result = parse_expand_param("user_account.user_groups,service_id.employees")
    assert result == ["user_account.user_groups", "service_id.employees"]
    print("  - Nested fields: PASS")


if __name__ == "__main__":
    print("Testing parse_expand_param function...")
    print("-" * 50)

    test_parse_expand_param_single_field()
    test_parse_expand_param_multiple_fields()
    test_parse_expand_param_with_spaces()
    test_parse_expand_param_empty()
    test_parse_expand_param_none()
    test_parse_expand_param_nested()

    print("-" * 50)
    print("All parse_expand_param tests passed!")
    print("\nNote: apply_expansion function exists andis used throughout")
    print("the codebase. It will be tested during integration tests.")
