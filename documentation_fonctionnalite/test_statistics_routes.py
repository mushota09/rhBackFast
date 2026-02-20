"""Test script for Statistics routes"""
from app.paie_app.routes import statistics_router


def test_statistics_routes():
    """Test that all statistics routes are registered"""
    expected_routes = [
        '/statistics/periode/{periode_id}/summary',
        '/statistics/annual/{annee}/summary',
        '/statistics/employee/{employe_id}/history',
        '/statistics/deductions/summary',
        '/statistics/alerts/summary',
        '/statistics/comparative/{annee}/{mois}',
        '/statistics/top-earners',
        '/statistics/dashboard',
    ]

    # Get all route paths
    route_paths = [route.path for route in statistics_router.routes]

    print("Registered Statistics Routes:")
    for path in route_paths:
        print(f"  ✓ {path}")

    # Check that all expected routes are present
    missing = []
    for expected in expected_routes:
        if expected not in route_paths:
            missing.append(expected)
            print(f"\n✗ Route {expected} is MISSING")
        else:
            print(f"\n✓ Route {expected} is registered")

    if missing:
        print(f"\n❌ {len(missing)} routes are missing")
        return False

    print(f"\n✅ All {len(expected_routes)} statistics routes are registered")
    return True


if __name__ == "__main__":
    result = test_statistics_routes()
    if result:
        print("\n🎉 Statistics routes test passed!")
    else:
        print("\n❌ Statistics routes test failed!")
