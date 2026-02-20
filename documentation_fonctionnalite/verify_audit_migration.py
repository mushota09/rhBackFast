"""Verify audit_log table structure after migration"""
import asyncio
from sqlalchemy import text, inspect
from app.core.database import engine


async def verify_audit_table():
    """Verify the audit_log table structure"""
    async with engine.connect() as conn:
        # Check if table exists
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'audit_log'
            );
        """))
        table_exists = result.scalar()
        print(f"✓ audit_log table exists: {table_exists}")

        if not table_exists:
            print("❌ audit_log table not found!")
            return

        # Check columns
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'audit_log'
            ORDER BY ordinal_position;
        """))
        columns = result.fetchall()
        print(f"\n✓ audit_log has {len(columns)} columns:")
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  - {col[0]}: {col[1]} ({nullable})")

        # Check indexes
        result = await conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'audit_log'
            ORDER BY indexname;
        """))
        indexes = result.fetchall()
        print(f"\n✓ audit_log has {len(indexes)} indexes:")
        for idx in indexes:
            print(f"  - {idx[0]}")

        # Check constraints
        result = await conn.execute(text("""
            SELECT conname, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'audit_log'::regclass
            ORDER BY conname;
        """))
        constraints = result.fetchall()
        print(f"\n✓ audit_log has {len(constraints)} constraints:")
        for con in constraints:
            print(f"  - {con[0]}")

        print("\n✅ Migration verification complete!")


if __name__ == "__main__":
    asyncio.run(verify_audit_table())
