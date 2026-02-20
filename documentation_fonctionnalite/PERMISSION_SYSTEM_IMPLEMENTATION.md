# Permission System Implementation

## Overview
Implemented a complete permission and authorization system for rhBackFast based on the rhBack Django implementation. The system provides group-based access control (RBAC) with granular permissions.

## Models Added/Updated

### Permission Model (`app/user_app/models.py`)
- **Table**: `user_management_permission`
- **Fields**:
  - `codename`: Unique permission identifier (e.g., "employee.view")
  - `name`: Human-readable permission name
  - `content_type`: ContentType ID (integer)
  - `resource`: Resource name (e.g., "employee", "payroll")
  - `action`: Action type (CREATE, READ, UPDATE, DELETE)
  - `description`: Detailed description
- **Constraints**:
  - Unique constraint on (resource, action)
  - Check constraint on action values
- **Relationships**:
  - `group_permissions`: One-to-ma
eated_by`: Many-to-one with User

## Schemas Added (`app/user_app/schemas.py`)

### Permission Schemas
- `PermissionBase`: Base schema with all fields
- `PermissionCreate`: For creating permissions
- `PermissionResponse`: Response schema with timestamps

### GroupPermission Schemas
- `GroupPermissionBase`: Base schema
- `GroupPermissionCreate`: For creating group permissions
- `GroupPermissionUpdate`: For updating granted flag
- `GroupPermissionResponse`: Response schema with timestamps
- `GroupPermissionFilter`: Filter parameters for listing
- `UserPermissionsResponse`: Response for user's effective permissions

## Services Added (`app/user_app/services.py`)

### PermissionService Class
Provides methods for permission management and checking:

#### `get_user_permissions(db, user_id) -> set[str]`
- Gets all permission codenames for a user based on group memberships
- Returns set of permission codenames (e.g., {'employe.view', 'user.create'})

#### `check_permission(db, user, resource, action) -> bool`
- Checks if a user has a specific permission
- Superusers automatically have all permissions
- Returns True if user has the permission

#### `get_effective_permissions(db, user_id) -> dict`
- Gets detailed information about user's effective permissions
- Returns groups, permissions, and counts
- Useful for displaying user's access rights

#### `create_group_permission(db, group_id, permission_id, granted, created_by_id) -> GroupPermission`
- Creates a group permission assignment
- Validates group and permission existence
- Prevents duplicate assignments

#### `list_group_permissions(db, group_id, permission_id, granted, skip, limit) -> Tuple[List, int]`
- Lists group permissions with filters
- Supports pagination
- Returns list and total count

## Routes Added (`app/user_app/routes.py`)

### Permission Routes (`/permissions`)
- `GET /permissions` - List all permissions (read-only)
- `GET /permissions/{id}` - Get permission by ID

### Group Permission Routes (`/group-permissions`)
- `GET /group-permissions` - List group permissions with filters
  - Query params: `group_id`, `permission_id`, `granted`, `skip`, `limit`
- `POST /group-permissions` - Create group permission
- `PUT /group-permissions/{id}` - Update group permission (granted flag)
- `DELETE /group-permissions/{id}` - Delete group permission
- `GET /group-permissions/users/{user_id}/permissions` - Get user's effective permissions

## Permission Codename Format
Permissions use the format: `resource.action`

Examples:
- `employe.view` - View employees
- `employe.create` - Create employees
- `employe.update` - Update employees
- `employe.delete` - Delete employees
- `user.create` - Create users
- `payroll.view` - View payroll data

## Usage Examples

### Check if user has permission
```python
from app.user_app.services import PermissionService

# Check permission
has_permission = await PermissionService.check_permission(
    db, user, "employe", "view"
)
```

### Get user's effective permissions
```python
permissions_data = await PermissionService.get_effective_permissions(db, user.id)
# Returns:
# {
#     'groups': [...],
#     'permissions': [...],
#     'permission_count': 10,
#     'group_count': 2
# }
```

### Create group permission
```python
group_permission = await PermissionService.create_group_permission(
    db,
    group_id=1,
    permission_id=5,
    granted=True,
    created_by_id=current_user.id
)
```

## Security Features

1. **Superuser Bypass**: Superusers automatically have all permissions
2. **Active User Check**: Only active users can have permissions
3. **Active Group Check**: Only permissions from active groups are considered
4. **Granted Flag**: Permissions can be explicitly granted or denied
5. **Audit Trail**: `created_by_id` tracks who assigned permissions

## Integration with Existing System

The permission system integrates seamlessly with:
- **User Model**: Users get permissions through group memberships
- **Group Model**: Groups have many permissions through GroupPermission
- **UserGroup Model**: Links users to groups
- **Authentication**: Works with existing JWT authentication

## Next Steps

To fully utilize the permission system:

1. **Create Initial Permissions**: Load permissions from fixtures or create via API
2. **Assign Permissions to Groups**: Configure which groups have which permissions
3. **Add Permission Checks to Routes**: Protect routes with permission checks
4. **Create Permission Decorator**: Build a decorator for easy route protection
5. **Add Permission UI**: Create frontend for managing permissions

## Testing

Run the test script to verify the implementation:
```bash
python test_permissions.py
```

## Differences from rhBack

1. **Async/Await**: All methods are async (rhBack uses sync_to_async)
2. **No Caching**: rhBackFast doesn't implement caching yet (can be added later)
3. **Simplified**: No audit logging yet (can be added later)
4. **ContentType**: Uses integer ID instead of Django's ContentType model

## Files Modified

- `rhBackFast/app/user_app/models.py` - Updated Permission and GroupPermission models
- `rhBackFast/app/user_app/schemas.py` - Added permission schemas
- `rhBackFast/app/user_app/services.py` - Added PermissionService class
- `rhBackFast/app/user_app/routes.py` - Added permission routes
