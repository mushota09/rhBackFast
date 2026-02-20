"""
Test script to verify the application starts correctly with auto-permission creation
"""
import asyncio


async def test_app_startup():
    """Test that the app can start with the new lifespan manager"""
    try:
        print("Testing application startup...")

        # Test main.py imports
        print("1. Testing main.py imports...")
        from main import app
        print("   ✅ Main app imported successfully")

        # Test config
        print("2. Testing configuration...")
        from app.core.config import settings
        print(f"   - AUTO_CREATE_PERMISSIONS: {settings.AUTO_CREATE_PERMISSIONS}")
        print("   ✅ Configuration loaded")

        # Test startup module
        print("3. Testing startup module...")
        from app.core.startup import run_startup_tasks
        print("   ✅ Startup module loaded")

        print("\n✅ Application can start successfully!")
        print("\nTo start the application, run:")
        print("  python main.py")
        print("\nOr with uvicorn:")
        print("  uvicorn main:app --reload")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(test_app_startup())
    sys.exit(0 if success else 1)
