"""Permission checking utilities for route protection"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.user_app.models import User
from app.user_app.services import PermissionService


def require_permission(resource: str, action: str):
    """
    Dependency factory to check if user has required permission

    Args:
        resource: Resource name (e.g., 'employe', 'user', 'payroll')
        action: Action name (e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE')

    Returns:
        Dependency function that checks permission and returns current user

    Usage:
        @router.get("/employees")
        async def list_employees(
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(require_permission("employe", "READ"))
        ):
            # User has permission, proceed with logic
            ...

    Raises:
        HTTPException: 403 Forbidden if user does not have permission
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Superusers bypass all permission checks
        if current_user.is_superuser:
            return current_user

        # Check if user has the required permission
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


async def check_permission_or_403(
    db: AsyncSession,
    user: User,
    resource: str,
    action: str
) -> None:
    """
    Helper function to check permission and raise 403 if denied

    Args:
        db: Database session
        user: Current user
        resource: Resource name
        action: Action name

    Raises:
        HTTPException: 403 Forbidden if user does not have permission

    Usage:
        async def some_function(db: AsyncSession, user: User):
            # Check permission inline
            await check_permission_or_403(db, user, "employe", "DELETE")

            # Proceed with logic
            ...
    """
    if user.is_superuser:
        return

    has_permission = await PermissionService.check_permission(
        db, user, resource, action
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {resource}.{action}"
        )
