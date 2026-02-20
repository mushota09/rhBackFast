# Permission System Integration Example

## Before and After: Protecting Routes with Permissions

### Example 1: Employee Routes

#### Before (No Permission Check)
```python
@employe_router.get("/", response_model=schemas.PaginatedResponse[schemas.EmployeResponse])
async def list_employees(
    poste_id: Optional[int] = Query(None),
    statut_emploi: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    expand: Optional[str] = Query(None),
    ordering: Optional[str] = Query('-id'),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all employees with filters, search, and pagination"""
    filters = schemas.EmployeFilter(
        poste_id=poste_id,
        statut_emploi=statut_emploi,
        search=search,
        expand=expand,
        skip=skip,
        limit=limit,
        ordering=ordering

    search: Optional[str] = Query(None),
    expand: Optional[str] = Query(None),
    ordering: Optional[str] = Query('-id'),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("employe", "READ"))  # ⭐ ADDED
):
    """List all employees with filters, search, and pagination

    Requires: employe.READ permission
    """
    filters = schemas.EmployeFilter(
        poste_id=poste_id,
        statut_emploi=statut_emploi,
        search=search,
        expand=expand,
        skip=skip,
        limit=limit,
        ordering=ordering
    )
    employees, total = await EmployeeService.list_with_filters(db, filters)
    return {
        "results": employees,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

### Example 2: Create Employee

#### Before
```python
@employe_router.post("/", response_model=schemas.EmployeResponse)
async def create_employee(
    employee: schemas.EmployeCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user)
):
    """Create a new employee (basic creation without user account)"""
    try:
        db_employee = await EmployeeService.create_employee(db, employee)
        await db.commit()
        await db.refresh(db_employee)
        return db_employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
```

#### After
```python
@employe_router.post("/", response_model=schemas.EmployeResponse)
async def create_employee(
    employee: schemas.EmployeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("employe", "CREATE"))  # ⭐ CHANGED
):
    """Create a new employee (basic creation without user account)

    Requires: employe.CREATE permission
    """
    try:
        db_employee = await EmployeeService.create_employee(db, employee)
        await db.commit()
        await db.refresh(db_employee)
        return db_employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
```

### Example 3: Delete Employee

#### Before
```python
@employe_router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user)
):
    """Delete employee"""
    from sqlalchemy import select
    result = await db.execute(
        select(Employe).where(Employe.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db.delete(employee)
    await db.commit()
    return {"message": "Employee deleted successfully"}
```

#### After
```python
@employe_router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("employe", "DELETE"))  # ⭐ CHANGED
):
    """Delete employee

    Requires: employe.DELETE permission
    """
    from sqlalchemy import select
    result = await db.execute(
        select(Employe).where(Employe.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db.delete(employee)
    await db.commit()
    return {"message": "Employee deleted successfully"}
```

## Complete Route Protection Pattern

### All Employee Routes Protected
```python
from app.core.permissions import require_permission

# READ permission
@employe_router.get("/")
async def list_employees(
    ...,
    current_user: User = Depends(require_permission("employe", "READ"))
):
    ...

@employe_router.get("/{employee_id}")
async def get_employee(
    ...,
    current_user: User = Depends(require_permission("employe", "READ"))
):
    ...

# CREATE permission
@employe_router.post("/")
async def create_employee(
    ...,
    current_user: User = Depends(require_permission("employe", "CREATE"))
):
    ...

@employe_router.post("/with-user")
async def create_employee_with_user(
    ...,
    current_user: User = Depends(require_permission("employe", "CREATE"))
):
    ...

@employe_router.post("/create-complete")
async def create_complete_employee(
    ...,
    current_user: User = Depends(require_permission("employe", "CREATE"))
):
    ...

# UPDATE permission
@employe_router.put("/{employee_id}")
async def update_employee(
    ...,
    current_user: User = Depends(require_permission("employe", "UPDATE"))
):
    ...

# DELETE permission
@employe_router.delete("/{employee_id}")
async def delete_employee(
    ...,
    current_user: User = Depends(require_permission("employe", "DELETE"))
):
    ...
```

## Permission Matrix

### Recommended Permissions by Resource

| Resource | Actions | Description |
|----------|---------|-------------|
| employe | CREATE, READ, UPDATE, DELETE | Employee management |
| user | CREATE, READ, UPDATE, DELETE | User account management |
| group | CREATE, READ, UPDATE, DELETE | Group management |
| service | CREATE, READ, UPDATE, DELETE | Service management |
| contrat | CREATE, READ, UPDATE, DELETE | Contract management |
| document | CREATE, READ, UPDATE, DELETE | Document management |
| permission | READ | Permission viewing (admin only) |
| group_permission | CREATE, READ, UPDATE, DELETE | Permission assignment (admin only) |

### Recommended Group Permissions

#### Admin Group (ADM)
- All permissions on all resources

#### HR Group (RRH)
- employe: CREATE, READ, UPDATE
- user: CREATE, READ, UPDATE
- contrat: CREATE, READ, UPDATE
- document: CREATE, READ, UPDATE
- group: READ

#### Manager Group (DIR)
- employe: READ
- contrat: READ
- document: READ
- group: READ

#### Employee Group (EMP)
- employe: READ (own profile only - requires object-level permissions)
- document: READ (own documents only - requires object-level permissions)

## Testing Permission Integration

### 1. Create Test Permissions
```bash
# Via API or database
POST /permissions
{
    "codename": "employe.read",
    "name": "Read Employee",
    "content_type": 1,
    "resource": "employe",
    "action": "READ",
    "description": "Permission to view employees"
}
```

### 2. Assign to Group
```bash
POST /group-permissions
{
    "group_id": 1,  # RRH group
    "permission_id": 1,  # employe.read
    "granted": true
}
```

### 3. Test Protected Route
```bash
# Without permission - should return 403
GET /employees
Authorization: Bearer <token_without_permission>

# With permission - should return 200
GET /employees
Authorization: Bearer <token_with_permission>
```

## Migration Checklist

- [ ] Create all required permissions in database
- [ ] Assign permissions to existing groups
- [ ] Update all routes to use `require_permission()`
- [ ] Update route docstrings with permission requirements
- [ ] Test each protected route
- [ ] Update API documentation
- [ ] Train users on new permission system

## Notes

1. **Superusers**: Always bypass permission checks
2. **Active Users**: Only active users can have permissions
3. **Active Groups**: Only permissions from active groups count
4. **Granted Flag**: Can explicitly deny permissions with `granted=False`
5. **Audit**: Track who assigns permissions via `created_by_id`
