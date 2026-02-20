"""
Integration tests for expand functionality in rhBackFast API

This test suite validates the expand parameter functionality across different endpoints,
ensuring that relations are properly loaded and serialized.

Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 6.1, 6.2, 6.3, 6.4
"""
import pytest
import pytest_asyncio
import httpx
from typing import Dict, Any


# ************************************************************************
# FIXTURES
# ************************************************************************

@pytest_asyncio.fixture
async def authenticated_client():
    """
    Provide an authenticated HTTP client for testing

    This fixture:
    1. Creates an async HTTP client
    2. Logs in with test credentials
    3. Extracts JWT token
    4. Sets Authorization header

    Requirements: 1.3, 1.4

    Note: Requires the application to be running on http://localhost:8000
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=5.0) as client:
        try:
            # Login to get JWT token
            response = await client.post("/api/auth/login", json={
                "email": "mushota09@gmail.com",
                "password": "rapha12345678"
            })

            # Verify login was successful
            assert response.status_code == 200, f"Login failed: {response.text}"

            token_data = response.json()
            assert "access" in token_data, "No access token in response"

            # Set authorization header for all subsequent requests
            client.headers["Authorization"] = f"Bearer {token_data['access']}"

            yield client
        except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadTimeout) as e:
            pytest.skip(f"Server not running on http://localhost:8000: {e}")


# ************************************************************************
# VALIDATION UTILITIES
# ************************************************************************

def assert_expanded(response_data: Dict[str, Any], field_name: str):
    """
    Verify that a field is expanded (object, not just ID)

    Checks:
    - Field exists in response
    - Field is a dict/object (not int)
    - Expanded object has required fields (id, created_at, updated_at)

    Requirements: 6.1, 6.4
    """
    assert field_name in response_data, f"Field '{field_name}' not found in response"

    field_value = response_data[field_name]
    assert isinstance(field_value, dict), \
        f"Field '{field_name}' should be expanded object (dict), got {type(field_value)}"

    # Check for required fields in expanded object
    assert "id" in field_value, f"Expanded '{field_name}' missing 'id' field"
    assert "created_at" in field_value, f"Expanded '{field_name}' missing 'created_at' field"
    assert "updated_at" in field_value, f"Expanded '{field_name}' missing 'updated_at' field"


def assert_not_expanded(response_data: Dict[str, Any], field_name: str):
    """
    Verify that a field is NOT expanded (ID only)

    Checks:
    - Field exists in response
    - Field is an integer ID (not object)

    Requirements: 2.1, 6.3
    """
    assert field_name in response_data, f"Field '{field_name}' not found in response"

    field_value = response_data[field_name]
    assert isinstance(field_value, int), \
        f"Field '{field_name}' should be integer ID, got {type(field_value)}"


def validate_response_structure(response: httpx.Response):
    """
    Validate the basic structure of an API response

    Checks:
    - Status code is 200
    - Response is valid JSON
    - Response has "results" and "total" keys

    Requirements: 6.2
    """
    assert response.status_code == 200, \
        f"Expected status 200, got {response.status_code}: {response.text}"

    try:
        data = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e}")

    assert "results" in data, "Response missing 'results' key"
    assert "total" in data, "Response missing 'total' key"
    assert isinstance(data["results"], list), "'results' should be a list"
    assert isinstance(data["total"], int), "'total' should be an integer"

    return data


# ************************************************************************
# TEST: Authentication Fixture
# ************************************************************************

@pytest.mark.asyncio
async def test_authentication_fixture(authenticated_client):
    """
    Test that the authentication fixture works correctly

    Verifies:
    - Fixture returns authenticated client
    - Client can access protected endpoints

    Requirements: 1.3
    """
    # Try to access a protected endpoint
    response = await authenticated_client.get("/api/auth/protected")

    assert response.status_code == 200, \
        f"Protected endpoint should be accessible with auth, got {response.status_code}"

    data = response.json()
    assert "user_id" in data, "Protected endpoint should return user_id"




# ************************************************************************
# TASK 4: USER-GROUPS EXPAND TESTS
# ************************************************************************

@pytest.mark.asyncio
async def test_user_groups_without_expand(authenticated_client):
    """
    Test user-groups endpoint without expand parameter

    Verifies:
    - GET /api/user-groups/ returns data
    - user_id and group_id are integers (not expanded)
    - Response structure is valid

    Requirements: 2.1
    """
    response = await authenticated_client.get("/api/user-groups/")

    # Validate response structure
    data = validate_response_structure(response)

    # Verify we have at least one result to test
    assert len(data["results"]) > 0, "No user-groups found in database"

    # Check first result
    user_group = data["results"][0]

    # Verify user_id and group_id are NOT expanded (should be integers)
    assert_not_expanded(user_group, "user_id")
    assert_not_expanded(user_group, "group_id")


@pytest.mark.asyncio
async def test_user_groups_expand_user(authenticated_client):
    """
    Test user-groups endpoint with expand=user

    Verifies:
    - GET /api/user-groups/?expand=user returns data
    - user field is expanded (object with details)
    - user object has required fields
    - group_id remains as integer (not expanded)

    Requirements: 2.2
    """
    response = await authenticated_client.get("/api/user-groups/?expand=user")

    # Validate response structure
    data = validate_response_structure(response)

    # Verify we have at least one result to test
    assert len(data["results"]) > 0, "No user-groups found in database"

    # Check first result
    user_group = data["results"][0]

    # Verify user is expanded
    assert_expanded(user_group, "user")

    # Verify user object has expected fields
    user = user_group["user"]
    assert "email" in user, "Expanded user should have 'email' field"
    assert "nom" in user, "Expanded user should have 'nom' field"

    # Verify group_id is NOT expanded (should still be integer)
    assert_not_expanded(user_group, "group_id")


@pytest.mark.asyncio
async def test_user_groups_expand_group(authenticated_client):
    """
    Test user-groups endpoint with expand=group

    Verifies:
    - GET /api/user-groups/?expand=group returns data
    - group field is expanded (object with details)
    - group object has required fields
    - user_id remains as integer (not expanded)

    Requirements: 2.3
    """
    response = await authenticated_client.get("/api/user-groups/?expand=group")

    # Validate response structure
    data = validate_response_structure(response)

    # Verify we have at least one result to test
    assert len(data["results"]) > 0, "No user-groups found in database"

    # Check first result
    user_group = data["results"][0]

    # Verify group is expanded
    assert_expanded(user_group, "group")

    # Verify group object has expected fields
    group = user_group["group"]
    assert "code" in group, "Expanded group should have 'code' field"
    assert "name" in group, "Expanded group should have 'name' field"

    # Verify user_id is NOT expanded (should still be integer)
    assert_not_expanded(user_group, "user_id")


@pytest.mark.asyncio
async def test_user_groups_expand_multiple(authenticated_client):
    """
    Test user-groups endpoint with expand=user,group

    Verifies:
    - GET /api/user-groups/?expand=user,group returns data
    - Both user and group fields are expanded
    - Both expanded objects have required fields

    Requirements: 2.4
    """
    response = await authenticated_client.get("/api/user-groups/?expand=user,group")

    # Validate response structure
    data = validate_response_structure(response)

    # Verify we have at least one result to test
    assert len(data["results"]) > 0, "No user-groups found in database"

    # Check first result
    user_group = data["results"][0]

    # Verify both user and group are expanded
    assert_expanded(user_group, "user")
    assert_expanded(user_group, "group")

    # Verify user object has expected fields
    user = user_group["user"]
    assert "email" in user, "Expanded user should have 'email' field"
    assert "nom" in user, "Expanded user should have 'nom' field"

    # Verify group object has expected fields
    group = user_group["group"]
    assert "code" in group, "Expanded group should have 'code' field"
    assert "name" in group, "Expanded group should have 'name' field"

