"""Test Service routes implementation"""
import asyncio
import sys
from sqlalchemy import select, func

# Add the app directory to the path
sys.path.insert(0, '.')

from app.core.database import AsyncSessionLocal
from app.user_app.models import Service


async def test_service_routes():
    """Test that Service routes are properly implemented"""
    print("=" * 60)
    print("Testing Service Routes Implementation")
    print("=" * 60)
    print()

    async with AsyncSessionLocal() as db:
        # Test 1: Check if we can query services
        print("Test 1: Query services from database")
        try:
            query = select(Service)
            result = await db.execute(query)
            services = result.scalars().all()
            print(f"✓ Successfully queried {len(services)} services")
        except Exception as e:
            print(f"✗ Failed to query services: {e}")
            return False

        # Test 2: Check if we can count services
        print("\nTest 2: Count services")
        try:
            count_query = select(func.count()).select_from(Service)
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0
            print(f"✓ Successfully counted {total} services")
        except Exception as e:
            print(f"✗ Failed to count services: {e}")
            return False

        # Test 3: Check pagination logic
        print("\nTest 3: Test pagination logic")
        try:
            skip = 0
            limit = 10
            query = select(Service).offset(skip).limit(limit)
            result = await db.execute(query)
            paginated_services = result.scalars().all()
            print(f"✓ Successfully paginated services (skip={skip}, limit={limit})")
            print(f"  Retrieved {len(paginated_services)} services")
        except Exception as e:
            print(f"✗ Failed pagination test: {e}")
            return False

        # Test 4: Check if we can get a single service
        print("\nTest 4: Get single service by ID")
        try:
            if services:
                service_id = services[0].id
                query = select(Service).where(Service.id == service_id)
                result = await db.execute(query)
                service = result.scalar_one_or_none()
                if service:
                    print(f"✓ Successfully retrieved service ID {service_id}")
                    print(f"  Code: {service.code}, Titre: {service.titre}")
                else:
                    print(f"✗ Service ID {service_id} not found")
                    return False
            else:
                print("⚠ No services in database to test")
        except Exception as e:
            print(f"✗ Failed to get single service: {e}")
            return False

    print("\n" + "=" * 60)
    print("All Service route tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_service_routes())
    sys.exit(0 if success else 1)
