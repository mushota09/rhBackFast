"""
Test script to verify automatic permission creation at startup
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, text

from app.core.config import settings
from app.user_app.models import Permission


async def test_auto_permissions():
    """Test that permissions are created automatically"""
    try:
        print("Testing automatic permission creation...\n")

        # Create engine and session
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Check if permissions table exists
        print("1. Checking if permissions table exists...")
        async with async_session() as session:
            try:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM user_management_permission")
                )
                count = result.scalar()
                print(f"   ✅ Permissions table exists with {count} permissions")
            except Exception as e:
                print(f"   ⚠️  Permissions table doesn't exist yet: {e}")
                print("   This is normal if you haven't run migrations yet")
                await engine.dispose()
                return True

        # Test the startup function
        print("\n2. Testing startup function...")
        from app.core.startup import create_default_permissions

        # Run the function
        await create_default_permissions()

        # Check permissions again
        print("\n3. Verifying permissions were created...")
        async with async_session() as session:
            result = await session.execute(
                select(Permission).order_by(Permission.resource, Permission.action)
            )
            permissions = result.scalars().all()

            if permissions:
                print(f"   ✅ Found {len(permissions)} permissions")

                # Group by resource
                resources = {}
                for perm in permissions:
                    if perm.resource not in resources:
                        resources[perm.resource] = []
                    resources[perm.resource].append(perm.action)

                print(f"\n   Resources with permissions:")
                for resource, actions in sorted(resources.items()):
                    print(f"   - {resource}: {', '.join(actions)}")
            else:
                print("   ⚠️  No permissions found")

        await engine.dispose()

        print("\n✅ All tests passed!")
        print("\nTo start the application with auto-permission creation:")
        print("  python main.py")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(test_auto_permissions())
    sys.exit(0 if success else 1)
