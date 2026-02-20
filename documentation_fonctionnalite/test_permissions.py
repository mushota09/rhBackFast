"""Test script for permission system"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.user_app.models import Permission, GroupPermission, Group, User
from app.user_app.services import PermissionService
from app.core.database import Base

# Test database URL
DATABASE_URL = "sqlite+aiosqlite:///./test_permissions.db"


async def test_permissions():
    """Test permission system"""
    # Create engine and session
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Create a test permission
        permission = Permission(
            codename="employee.view",
            name="View Employee",
            content_type=1,
            resource="employee",
            action="READ",
            description="Permission to view employees"
        )
        session.add(permission)
        await session.flush()

        # Create a test group
        group = Group(
            code="TEST",
            name="Test Group",
            description="Test group for permissions",
            is_active=True
        )
        session.add(group)
        await session.flush()

        # Create group permission
        group_permission = await PermissionService.create_group_permission(
            session,
            group_id=group.id,
            permission_id=permission.id,
            granted=True
        )

        await session.commit()

        print(f"✓ Created permission: {permission}")
        print(f"✓ Created group: {group}")
        print(f"✓ Created group permission: {group_permission}")

        # List group permissions
        group_permissions, total = await PermissionService.list_group_permissions(
            session,
            group_id=group.id
        )
        print(f"✓ Found {total} group permissions")

    print("\n✅ All permission tests passed!")


if __name__ == "__main__":
    asyncio.run(test_permissions())
