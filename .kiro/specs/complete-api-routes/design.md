# Design Document: Complete API Routes

## Overview

This design document outlines the approach for completing and correcting the API routes in rhBackFast. The solution focuses on fixing syntax errors, adding missing imports, and ensuring all CRUD routes have consistent pagination and expansion support.

## Architecture

### Current State
- FastAPI application with multiple routers for different models
- Partial implementation of pagination and expand functionality
- Missing imports causing runtime errors
- Inconsistent route implementations across models

### Target State
- All routes with consistent pagination support (skip, limit, no_pagination)
- All GET routes with expand parameter support for loading relations
- Clean, error-free code with proper imports
- Consistent response format across all endpoints

## Components and Interfaces

### 1. Import Corrections

**Module:** `app/user_app/routes.py`

**Required Imports:**
```python
from sqlalchemy import select, func
```

The `func` module is needed for count queries in pagination.

### 2. Query Utilities

**Module:** `app/core/query_utils.py`

**Functions:**
- `parse_expand_param(expand: str) -> List[str]`: Parse comma-separated expand parameter
- `apply_expansion(query, model, expand_fields: List[str])`: Apply SQLAlchemy eager loading

These utilities are already referenced in the code and should exist or be created.

### 3. Pagination Pattern

**Standard Pagination Response:**
```python
{
    "results": [...],
    "total": int,
    "skip": int,
    "limit": int
}
```

**No Pagination Response:**
```python
{
    "results": [...],
    "total": int
}
```

**Implementation Pattern:**
```python
# Get total count
count_query = select(func.count()).select_from(Model)
total_result = await db.execute(count_query)
total = total_result.scalar() or 0

# Apply pagination if requested
if not no_pagination:
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    return {
        "results": list(items),
        "total": total,
        "skip": skip,
        "limit": limit
    }
else:
    result = await db.execute(query)
    items = result.scalars().all()
    return {
        "results": list(items),
        "total": total
    }
```

### 4. Expand Pattern

**Implementation Pattern:**
```python
from app.core.query_utils import parse_expand_param, apply_expansion

query = select(Model)

# Apply expansion
if expand:
    expand_fields = parse_expand_param(expand)
    query = apply_expansion(query, Model, expand_fields)

result = await db.execute(query)
```

### 5. Route Structure

Each model should have the following routes:

**List Route:**
- Method: GET
- Path: `/models`
- Parameters: skip, limit, no_pagination, expand, filters
- Response: Paginated list with total count

**Create Route:**
- Method: POST
- Path: `/models`
- Body: Model creation schema
- Response: Created model

**Get Route:**
- Method: GET
- Path: `/models/{id}`
- Parameters: expand
- Response: Single model

**Update Route:**
- Method: PUT
- Path: `/models/{id}`
- Body: Model update schema
- Response: Updated model

**Delete Route:**
- Method: DELETE
- Path: `/models/{id}`
- Response: Success message

## Data Models

The following models need complete routes:

1. **Service** - Already has routes, needs syntax fixes
2. **Group** - Already has routes, needs consistency
3. **ServiceGroup** - Already has routes, needs syntax fixes
4. **User** - Has syntax errors, needs fixes
5. **UserGroup** - Already has routes, needs consistency
6. **Permission** - Partially implemented, needs POST route
7. **GroupPermission** - Already has routes, needs consistency
8. **Employe** - Already has routes, needs consistency
9. **Contrat** - Has syntax errors, needs fixes
10. **Document** - Already has routes, needs consistency

## Correctness Properties

*A property is a characteristic or behav
e, the response should include results, total, skip, and limit fields
**Validates: Requirements 2.1, 2.2, 2.4**

### Prop
LETE routes
**Validates: Requirements 4-13**

### Property 6: Syntax Validity
*For any* Python file in the routes module, the file should parse without syntax errors
**Validates: Requirements 1.2**

## Error Handling

### Validation Errors
- Return 400 Bad Request for invalid input data
- Include descriptive error messages

### Not Found Errors
- Return 404 Not Found when entity doesn't exist
- Include entity type in error message

### Database Errors
- Catch and handle SQLAlchemy exceptions
- Return 500 Internal Server Error for unexpected errors

## Testing Strategy

### Un
it Tests
- Test pagination logic with different skip/limit values
- Test no_pagination flag behavior
- Test expand parameter parsing
- Test filter application
- Test error handling for invalid IDs

### Property-Based Tests
- Generate random pagination parameters and verify response structure
- Generate random expand parameters and verify query construction
- Generate random model data and verify CRUD operations

**Testing Configuration:**
- Use pytest for unit tests
- Use Hypothesis for property-based tests
- Minimum 100 iterations per property test
- Tag format: **Feature: complete-api-routes, Property {number}: {property_text}**

### Integration Tests
- Test complete request/response cycle for each endpoint
- Test authentication and authorization
- Test database transactions and rollbacks
