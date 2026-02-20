"""Test that the audit_log table works with the database"""
import asyncio
from sqlalchemy import text
from app.core.database import engine


async def test_audit_table():
    """Test that the audit_log table exists and can be used"""
    async with engine.connect() as conn:
        try:
            # Insert a test record
            result = await conn.execute(text("""
                INSERT INTO audit_log (
                    action, resource_type, resource_id,
                    new_values, ip_address, user_agent,
                    request_method, request_path, response_status,
                    execution_time, timestamp
                ) VALUES (
                    'CREATE', 'test', '123',
                    '{"test": "data"}'::jsonb, '127.0.0.1'::inet, 'Test Agent',
                    'POST', '/api/test', 201,
                    0.123, NOW()
                )
                RETURNING id, action, resource_type, timestamp;
            """))
            row = result.fetchone()

            print(f"✅ Created audit log with ID: {row[0]}")
            print(f"   Action: {row[1]}")
            print(f"   Resource: {row[2]}")
            print(f"   Timestamp: {row[3]}")

            # Query it back
            result = await conn.execute(text("""
                SELECT id, action, resource_type, new_values
                FROM audit_log
                WHERE id = :id
            """), {"id": row[0]})
            retrieved = result.fetchone()

            print(f"\n✅ Retrieved audit log:")
            print(f"   ID: {retrieved[0]}")
            print(f"   Action: {retrieved[1]}")
            print(f"   Resource: {retrieved[2]}")
            print(f"   New Values: {retrieved[3]}")

            # Test the check constraint
            try:
                await conn.execute(text("""
                    INSERT INTO audit_log (
                        action, resource_type, timestamp
                    ) VALUES (
                        'INVALID_ACTION', 'test', NOW()
                    );
                """))
                print("\n❌ Check constraint failed - invalid action was allowed!")
            except Exception:
                print(f"\n✅ Check constraint working - invalid action rejected")

            # Clean up
            await conn.execute(text("""
                DELETE FROM audit_log WHERE id = :id
            """), {"id": row[0]})
            await conn.commit()

            print(f"\n✅ Cleaned up test data")
            print("\n🎉 audit_log table works correctly!")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await conn.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(test_audit_table())
