"""Test database connection"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def test_connection():
    """Test if database connection works"""
    print("Testing database connection...")

    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()

            if row and row[0] == 1:
                print("✅ Database connection successful!")

                # Test audit_log table exists
                result = await session.execute(
                    text("SELECT COUNT(*) FROM audit_log")
                )
                count = result.scalar()
                print(f"✅ audit_log table exists with {count} records")

                return True
            else:
                print("❌ Database connection failed: unexpected result")
                return False

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
