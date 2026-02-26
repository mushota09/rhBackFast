"""
Test script for bulk operations endpoints

This script tests the three new bulk operation endpoints:
1. POST /api/user-groups/bulk-assign/
2. POST /api/user-groups/bulk-remove/
3. POST /api/group-permissions/bulk-update/{group_id}/

Run this script after starting the FastAPI server to verify the endpoints work correctly.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

# Test credentials (adjust as needed)
TEST_EMAIL = "admin@example.com"
TEST_PASSWORD = "admin123"


def get_auth_token() -> str:
    """Authenticate and get access token"""
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access"]
    else:
        raise Exception(f"Authentication failed: {response.text}")


def get_headers(token: str) -> Dict[str, str]:
    """Get headers with authentication token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def test_bulk_assign_users_to_groups(token: str):
    """Test bulk assign users to groups endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Bulk Assign Users to Groups")
    print("="*80)
    
    # Test data - adjust IDs based on your database
    data = {
        "user_ids": [1, 2],
        "group_ids": [1, 2],
        "is_active": True,
        "replace_existing": False
    }
    
    print(f"\nRequest Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/user-groups/bulk-assign/",
        headers=get_headers(token),
        json=data
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n✅ TEST PASSED: Bulk assign successful")
    else:
        print("\n❌ TEST FAILED: Bulk assign failed")
    
    return response.status_code == 201


def test_bulk_update_group_permissions(token: str):
    """Test bulk update group permissions endpoint"""
    print("\n" + "="*80)
    print("TEST 2: Bulk Update Group Permissions")
    print("="*80)
    
    # Test data - adjust IDs based on your database
    group_id = 1
    data = {
        "permissions": [
            {"permission_id": 1, "granted": True},
            {"permission_id": 2, "granted": False},
            {"permission_id": 3, "granted": True}
        ]
    }
    
    print(f"\nGroup ID: {group_id}")
    print(f"Request Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/group-permissions/bulk-update/{group_id}/",
        headers=get_headers(token),
        json=data
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ TEST PASSED: Bulk update successful")
    else:
        print("\n❌ TEST FAILED: Bulk update failed")
    
    return response.status_code == 200


def test_bulk_remove_users_from_groups(token: str):
    """Test bulk remove users from groups endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Bulk Remove Users from Groups")
    print("="*80)
    
    # Test data - adjust IDs based on your database
    data = {
        "user_ids": [1, 2],
        "group_ids": [1, 2]
    }
    
    print(f"\nRequest Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/user-groups/bulk-remove/",
        headers=get_headers(token),
        json=data
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ TEST PASSED: Bulk remove successful")
    else:
        print("\n❌ TEST FAILED: Bulk remove failed")
    
    return response.status_code == 200


def test_validation_errors(token: str):
    """Test validation error handling"""
    print("\n" + "="*80)
    print("TEST 4: Validation Error Handling")
    print("="*80)
    
    # Test with invalid user IDs
    data = {
        "user_ids": [99999],  # Non-existent user
        "group_ids": [1],
        "is_active": True,
        "replace_existing": False
    }
    
    print(f"\nRequest Data (with invalid user ID): {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/user-groups/bulk-assign/",
        headers=get_headers(token),
        json=data
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201 and not response.json().get("success"):
        print("\n✅ TEST PASSED: Validation errors handled correctly")
        return True
    else:
        print("\n❌ TEST FAILED: Validation errors not handled correctly")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("BULK OPERATIONS ENDPOINT TESTS")
    print("="*80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Prefix: {API_PREFIX}")
    
    try:
        # Authenticate
        print("\nAuthenticating...")
        token = get_auth_token()
        print("✅ Authentication successful")
        
        # Run tests
        results = []
        results.append(("Bulk Assign Users to Groups", test_bulk_assign_users_to_groups(token)))
        results.append(("Bulk Update Group Permissions", test_bulk_update_group_permissions(token)))
        results.append(("Bulk Remove Users from Groups", test_bulk_remove_users_from_groups(token)))
        results.append(("Validation Error Handling", test_validation_errors(token)))
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
