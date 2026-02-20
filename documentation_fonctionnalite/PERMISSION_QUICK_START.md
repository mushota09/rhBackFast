# Permission System Quick Start Guide

## 1. Create Permissions

You have two options to create permissions:

### Option A: Automatic Creation (Recommended for Development)

Permissions are created automatically when the application starts if `AUTO_CREATE_PERMISSIONS=True` in your `.env` file.

```bash
# In your .env file
AUTO_CREATE_PERMISSIONS=True

# Start the application
python main.py

# Permissions are created automatically!
```

See [AUTO_PERMISSION_CREATION.md](./AUTO_PERMISSION_CREATION.md) for details.

### Option B: Manual Creation

Use the `create_permissions.py` script:

```bash
# Create all CRUD permissions for all models
python create_permissions.py create

# List all permissions
python create_permissions.py list

# Delete all permissions (use with caution!)
python create_permissions.py delete
```

### Permission Structure

First, create permissions for your resources:

```python
# Example: Create employee permissions
permissions = [
    {
        "codename": "employe.create",
        "name": "Create Employee",
        "content_type": 1,
        "resource": "employe",
        "action": "CREATE",
        "description": "Permission to create new employees"
    },
    {
        "codename": "employe.view",
        "name": "View Employee",
        "content_type": 1,
        "resource": "employe",
        "action": "READ",
        "description": "Permission to view employees"
    },
    {
        "codename": "employe.update",
        "name": "Update Employee",
        "content_type": 1,
        "resource": "employe",
        "action": "UPDATE",
        "description": "Permission to update employees"
    },
    {
        "codename": "employe.delete",
        "name": "Delete Employee",
        "content_type": 1,
        "resource": "employe",
        "action": "DELETE",
ew = await PermissionService.check_permission(
    db, current_user, "employe", "READ"
)

if not can_view:
    raise HTTPException(status_code=403, detail="Permission denied")
```

### Get All User Permissions

```python
# Get user's effective permissions
permissions = await PermissionService.get_effective_permissions(db, user.id)

print(f"User has {permissions['permission_count']} permissions")
print(f"User is in {permissions['group_count']} groups")
```

## 4. Protect Routes with Permissions

### Create Permission Dependency

```python
# app/core/permissions.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.user_app.models import User
from app.user_app.services import PermissionService


def require_permission(resource: str, action: str):
    """
    Dependency to check if user has required permission

    Usage:
        @router.get("/employees")
        async def list_employees(
            user: User = Depends(require_permission("employe", "READ"))
        ):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Superusers bypass permission checks
        if current_user.is_superuser:
            return current_user

        # Check permission
        has_permission = await PermissionService.check_permission(
            db, current_user, resource, action
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {resource}.{action}"
            )

        return current_user

    return permission_checker
```

### Use in Routes

```python
from app.core.permissions import require_permission

@employe_router.get("/")
async def list_employees(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("employe", "READ"))
):
    """List employees - requires employe.READ permission"""
    # User has permission, proceed
    ...

@employe_router.post("/")
async def create_employee(
    employee: EmployeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("employe", "CREATE"))
):
    """Create employee - requires employe.CREATE permission"""
    # User has permission, proceed
    ...
```

## 5. Common Permission Patterns

### Resource-Based Permissions

```python
# Standard CRUD permissions for a resource
RESOURCE_PERMISSIONS = {
    "CREATE": f"{resource}.create",
    "READ": f"{resource}.view",
    "UPDATE": f"{resource}.update",
    "DELETE": f"{resource}.delete"
}
```

### Hierarchical Permissions

```python
# Check multiple permissions
async def can_manage_employees(db, user):
    """Check if user can fully manage employees"""
    actions = ["CREATE", "READ", "UPDATE", "DELETE"]
    for action in actions:
        if not await PermissionService.check_permission(db, user, "employe", action):
            return False
    return True
```

### Permission Groups

```python
# Define permission groups for common roles
ADMIN_PERMISSIONS = [
    "employe.create", "employe.view", "employe.update", "employe.delete",
    "user.create", "user.view", "user.update", "user.delete",
    "group.create", "group.view", "group.update", "group.delete"
]

RRH_PERMISSIONS = [
    "employe.create", "employe.view", "employe.update",
    "contrat.create", "contrat.view", "contrat.update",
    "document.create", "document.view"
]

EMPLOYEE_PERMISSIONS = [
    "employe.view",  # Can view own profile
    "document.view"  # Can view own documents
]
```

## 6. API Endpoints

### List Permissions
```http
GET /permissions?skip=0&limit=100
```

### Get Permission
```http
GET /permissions/{permission_id}
```

### List Group Permissions
```http
GET /group-permissions?group_id=1&granted=true
```

### Create Group Permission
```http
POST /group-permissions
Content-Type: application/json

{
    "group_id": 1,
    "permission_id": 5,
    "granted": true
}
```

### Update Group Permission
```http
PUT /group-permissions/{id}
Content-Type: application/json

{
    "granted": false
}
```

### Delete Group Permission
```http
DELETE /group-permissions/{id}
```

### Get User Permissions
```http
GET /group-permissions/users/{user_id}/permissions
```

## 7. Best Practices

1. **Use Descriptive Codenames**: Follow the `resource.action` pattern
2. **Document Permissions**: Add clear descriptions to each permission
3. **Group Permissions Logically**: Organize permissions by resource/module
4. **Test Permission Checks**: Always test both granted and denied scenarios
5. **Audit Permission Changes**: Track who assigns/removes permissions
6. **Use Superuser Sparingly**: Only for system administrators
7. **Regular Permission Reviews**: Periodically review and update group permissions

## 8. Troubleshooting

### User has no permissions
- Check if user is in any active groups
- Verify groups have permissions assigned
- Ensure permissions are granted (not denied)

### Permission check fails
- Verify permission exists in database
- Check permission codename format
- Ensure user is active

### Superuser can't access
- Verify `is_superuser` flag is True
- Check if user is active

## 9. Migration from rhBack

If migrating from rhBack:

1. Export permissions from rhBack:
   ```bash
   python manage.py dumpdata user_app.permission > permissions.json
   ```

2. Export group permissions:
   ```bash
   python manage.py dumpdata user_app.grouppermission > group_permissions.json
   ```

3. Convert and import to rhBackFast (create migration script)

## 10. Future Enhancements

- [ ] Add caching for permission checks
- [ ] Implement permission inheritance
- [ ] Add object-level permissions
- [ ] Create permission audit log
- [ ] Build permission management UI
- [ ] Add permission templates
- [ ] Implement role-based permission sets
