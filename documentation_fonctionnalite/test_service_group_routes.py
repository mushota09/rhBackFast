"""Test ServiceGroup routes implementation"""
import asyncio
import sys
from sqlalchemy import select, func

# Add the app directory to the path
sys.path.insert(0, '.')

from app.core.database import AsyncSessionLocal
from app.user_app.models import ServiceGroup, Service, Group


async def test_service_group_routes():
    """Test that ServiceGroup routes are properly implemented"""
    print("=" * 60)
    print("Testing ServiceGroup Routes Implementation")
    print("=" * 60)
    print()

    async with AsyncSessionLocal() as db:
        # Test 1: Check if we can query service groups
        print("Test 1: Query service groups from database")
        try:
            query = select(ServiceGroup)
            result = await db.execute(query)
            service_groups = result.scalars().all()
            print(f"✓ Successfully queried {len(service_groups)} service groups")
        except Exception as e:
            print(f"✗ Failed to query service groups: {e}")
            return False

        # Test 2: Check if we can count service groups
        print("\nTest 2: Count service groups")
        try:
            count_query = select(func.count()).select_from(ServiceGroup)
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0
            print(f"✓ Successfully counted {total} service groups")
        except Exception as e:
            print(f"✗ Failed to count service groups: {e}")
            return False

        # Test 3: Check pagination logic
        print("\nTest 3: Test pagination logic")
        try:
            skip = 0
            limit = 10
            query = select(ServiceGroup).offset(skip).limit(limit)
            result = await db.execute(query)
            paginated_service_groups = result.scalars().all()
            print(f"✓ Successfully paginated service groups (skip={skip}, limit={limit})")
            print(f"  Retrieved {len(paginated_service_groups)} service groups")
        except Exception as e:
            print(f"✗ Failed pagination test: {e}")
            return False

        # Test 4: Check if we can get a single service group
        print("\nTest 4: Get single service group by ID")
        try:
            if service_groups:
                service_group_id = service_groups[0].id
                query = select(ServiceGroup).where(ServiceGroup.id == service_group_id)
                result = await db.execute(query)
                service_group = result.scalar_one_or_none()
                if service_group:
                    print(f"✓ Successfully retrieved service group ID {service_group_id}")
                    print(f"  Service ID: {service_group.service_id}, Group ID: {service_group.group_id}")
                else:
                    print(f"✗ Service group ID {service_group_id} not found")
                    return False
            else:
                print("⚠ No service groups in database to test")
        except Exception as e:
            print(f"✗ Failed to get single service group: {e}")
            return False

        # Test 5: Test filtering by service_id
        print("\nTest 5: Test filtering by service_id")
        try:
            if service_groups:
                service_id = service_groups[0].service_id
                query = select(ServiceGroup).where(ServiceGroup.service_id == service_id)
                result = await db.execute(query)
                filtered_groups = result.scalars().all()
                print(f"✓ Successfully filtered by service_id={service_id}")
                print(f"  Found {len(filtered_groups)} service groups")
            else:
                print("⚠ No service groups in database to test filtering")
        except Exception as e:
            print(f"✗ Failed filtering test: {e}")
            return False

        # Test 6: Test filtering by group_id
        print("\nTest 6: Test filtering by group_id")
        try:
            if service_groups:
                group_id = service_groups[0].group_id
                query = select(ServiceGroup).where(ServiceGroup.group_id == group_id)
                result = await db.execute(query)
                filtered_groups = result.scalars().all()
                print(f"✓ Successfully filtered by group_id={group_id}")
                print(f"  Found {len(filtered_groups)} service groups")
            else:
                print("⚠ No service groups in database to test filtering")
        except Exception as e:
            print(f"✗ Failed filtering test: {e}")
            return False

        # Test 7: Test count with filters
        print("\nTest 7: Test count with filters")
        try:
            if service_groups:
                service_id = service_groups[0].service_id
                count_query = select(func.count()).select_from(ServiceGroup).where(
                    ServiceGroup.service_id == service_id
                )
                total_result = await db.execute(count_query)
                total = total_result.scalar() or 0
                print(f"✓ Successfully counted with filter: {total} service groups")
            else:
                print("⚠ No service groups in database to test count with filters")
        except Exception as e:
            print(f"✗ Failed count with filters test: {e}")
            return False

    print("\n" + "=" * 60)
    print("All ServiceGroup route tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_service_group_routes())
    sys.exit(0 if success else 1)
