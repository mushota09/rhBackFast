"""Test audit integration in routes"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.audit_app.models import AuditLog


async def test_audit_logs_exist():
    """Test that audit logs table exists and can be queried"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10)
        )
        logs = result.scalars().all()

        print(f"Found {len(logs)} audit logs in the database")

        if logs:
            print("\nMost recent audit logs:")
            for log in logs[:5]:
                action = log.action
                resource = log.resource_type
                user = log.user_id
                print(f"  - {action} on {resource} by user {user}")
        else:
            print("\nNo audit logs found yet.")

        return True


async def main():
    """Main test function"""
    print("Testing audit integration...\n")

    try:
        await test_audit_logs_exist()
        print("\nAudit integration test passed!")
    except Exception as e:
        print(f"\nAudit integration test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
