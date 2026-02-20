"""Integration tests for API endpoints"""
import urllib.request
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            status = response.status
            content = response.read()

        success = status == 200
        icon = "OK" if success else "FAIL"
        print(f"{icon} {name} - Status: {status}")

        if success and content:
            data = json.loads(content)
            if isinstance(data, list):
                print(f"   Results: {len(data)} items")
        print()
        return success
    except Exception as e:
        print(f"FAIL {name} - Error: {str(e)}")
        print()
        return False

def main():
    print("=" * 60)
    print("API Integration Tests")
    print("=" * 60)
    print()

    tests = [
        ("Permissions", f"{BASE_URL}/api/permissions/?skip=0&limit=10"),
        ("Services", f"{BASE_URL}/api/services/?skip=0&limit=10"),
        ("Groups", f"{BASE_URL}/api/groups/?skip=0&limit=10"),
        ("Employees", f"{BASE_URL}/api/employees/?skip=0&limit=10"),
        ("Audit Logs", f"{BASE_URL}/api/audit/?skip=0&limit=10"),
        ("Paie Alerts", f"{BASE_URL}/api/paie/alerts/?skip=0&limit=10"),
        ("Paie Retenues", f"{BASE_URL}/api/paie/retenues/?skip=0&limit=10"),
        ("Paie Periodes", f"{BASE_URL}/api/paie/periodes/?skip=0&limit=10"),
        ("Paie Entrees", f"{BASE_URL}/api/paie/entrees/?skip=0&limit=10"),
        ("Paie Statistics", f"{BASE_URL}/api/paie/statistics/overview"),
        ("Paie History", f"{BASE_URL}/api/paie/history/?skip=0&limit=10"),
    ]

    results = [test_endpoint(name, url) for name, url in tests]

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
