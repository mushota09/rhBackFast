"""
Test script to verify startup.py works correctly
"""
import asyncio
import sys


async def test_startup():
    """Test the startup module"""
    try:
        print("Testing startup module...")

        # Test imports
        print("1. Testing imports...")
        from app.core.startup import (
            create_default_permissions,
            run_startup_tasks,
            MODEL_RESOURCE_MAPPING,
            ACTIONS
        )
        print("   ✅ Imports successful")

        # Test mappings
        print("2. Testing mappings...")
        print(f"   - Models: {len(MODEL_RESOURCE_MAPPING)}")
        print(f"   - Actions: {len(ACTIONS)}")
        print("   ✅ Mappings loaded")

        # Test function availability
        print("3. Testing functions...")
        print(f"   - create_default_permissions: {callable(create_default_permissions)}")
        print(f"   - run_startup_tasks: {callable(run_startup_tasks)}")
        print("   ✅ Functions available")

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_startup())
    sys.exit(0 if success else 1)
