# Expand Integration Tests

## Overview

This document describes the integration tests for the expand functionality in the rhBackFast API. These tests validate that the `expand` query parameter correctly loads and serializes related objects across different endpoints.

## Prerequisites

Before running these tests, ensure:

1. **Application is running**: The FastAPI application must be running on `http://localhost:8000`
   ```bash
   # Start the application
   uvicorn main:app --reload
   ```

2. **Test user exists**: The test user must exist in the database:
   - Email: `mushota09@gmail.com`
   - Password: `rapha12345678`

3. **Test data exists**: The database should contain:
   - At least one UserGroup record
   - Related User and Group records
   - (For future tests) ServiceGroup, Employee, and other related records

## Running the Tests

### Run all expand integration tests
```bash
pytest test_expand_integration.py -v
```

### Run specific test groups
```bash
# Run only user-groups tests
pytest test_expand_integration.py -k "user_groups" -v

# Run only authentication tests
pytest test_expand_integration.py -k "authentication" -v
```

### Run a specific test
```bash
pytest test_expand_integration.py::test_user_groups_without_expand -v
```

## Test Structure

The test file (`test_expand_integration.py`) contains:

### Fixtures
- `authenticated_client`: Provides an authenticated HTTP client with JWT token

### Validation Utilities
- `assert_expanded()`: Verifies a field is expanded (object, not ID)
- `assert_not_expanded()`: Verifies a field is NOT expanded (ID only)
- `validate_response_structure()`: Validates basic API response structure

### Test Groups

#### Task 4: User-Groups Expand Tests
- `test_user_groups_without_expand`: Tests default behavior (no expansion)
- `test_user_groups_expand_user`: Tests expanding the user relation
- `test_user_groups_expand_group`: Tests expanding the group relation
- `test_user_groups_expand_multiple`: Tests expanding multiple relations

## Expected Behavior

### When Server is Not Running
Tests will be **skipped** with a message indicating the server is not available:
```
SKIPPED [1] test_expand_integration.py:20: Server not running on http://localhost:8000
```

### When Server is Running
Tests will execute and validate:
- Response structure (status code, JSON format, required keys)
- Expansion behavior (IDs vs objects)
- Expanded object completeness (required fields present)

## Troubleshooting

### Tests are skipped
- **Cause**: Application is not running on `http://localhost:8000`
- **Solution**: Start the application with `uvicorn main:app --reload`

### Authentication fails
- **Cause**: Test user doesn't exist or password is incorrect
- **Solution**: Verify the test user exists in the database with correct credentials

### No user-groups found
- **Cause**: Database doesn't contain any UserGroup records
- **Solution**: Create test data or use an existing database with data

### Tests timeout
- **Cause**: Server is slow to respond or network issues
- **Solution**: Check server logs, increase timeout in fixture if needed

## Requirements Validation

These tests validate the following requirements from the design document:

- **Requirement 1.3, 1.4**: Authentication infrastructure
- **Requirement 2.1**: Non-expandedrelations return IDs
- **Requirement 2.2**: Expanding user relation
- **Requirement 2.3**: Expanding group relation
- **Requirement 2.4**: Expanding multiple relations
- **Requirement 6.1, 6.4**: Expanded data includes required fields
- **Requirement 6.2**: Response structure is valid JSON
- **Requirement 6.3**: Non-expanded fields are integers

## Next Steps

Additional test groups to be implemented:
- Task 5: Service-Groups expand tests
- Task 6: Employees expand tests
- Task 7: Nested expand tests
- Task 8: Error handling tests

