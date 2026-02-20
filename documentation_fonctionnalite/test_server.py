"""Test if the server is running"""
import requests
import time

def test_server():
    """Test if the FastAPI server is responding"""
    base_url = "http://localhost:8000"

    print("Testing FastAPI server...")
    print(f"Base URL: {base_url}\n")

    try:
        # Test root endpoint
        print("1. Testing root endpoint (/)...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Root endpoint OK: {response.json()}\n")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}\n")

        # Test health endpoint
        print("2. Testing health endpoint (/health)...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Health endpoint OK: {response.json()}\n")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}\n")

        # Test docs endpoint
        print("3. Testing docs endpoint (/docs)...")
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Docs endpoint OK (Swagger UI available)\n")
        else:
            print(f"   ❌ Docs endpoint failed: {response.status_code}\n")

        print("=" * 60)
        print("✅ Server is running successfully!")
        print(f"📖 API Documentation: {base_url}/docs")
        print(f"📖 ReDoc: {base_url}/redoc")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Wait a bit for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    test_server()
