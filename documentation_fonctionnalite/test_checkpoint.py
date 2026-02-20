"""Checkpoint test to verify routes and utilities"""

from app.core.query_utils import parse_expand_param, apply_expansion
from app.user_app.models import Service

def test_query_utils():
    """Test query utilities"""
    # Test parse_expand_param
    result = parse_expand_param('service,group')
    assert result == ['service', 'group'], f"Expected ['service', 'group'], got {result}"
    print("✓ parse_expand_param works correctly")

    # Test that apply_expansion exists and is callable
    assert callable(apply_expansion), "apply_expansion should be callable"
    print("✓ apply_expansion is callable")

def test_router_imports():
    """Test that all routers canbe imported"""
    from app.user_app.routes import (
        service_router, group_router, service_group_router,
        user_router, user_group_router, permission_router,
        group_permission_router, employe_router, contrat_router,
        document_router
    )

    routers = {
        'service_router': service_router,
        'group_router': group_router,
        'service_group_router': service_group_router,
        'user_router': user_router,
        'user_group_router': user_group_router,
        'permission_router': permission_router,
        'group_permission_router': group_permission_router,
        'employe_router': employe_router,
        'contrat_router': contrat_router,
        'document_router': document_router
    }

    print("\n✓ All routers imported successfully")
    print("\nRouter Summary:")
    for name, router in routers.items():
        route_count = len(router.routes)
        print(f"  {name}: {route_count} routes")

if __name__ == "__main__":
    print("=" * 60)
    print("Checkpoint Verification Tests")
    print("=" * 60)
    print()

    try:
        test_query_utils()
        print()
        test_router_imports()
        print()
        print("=" * 60)
        print("✅ All checkpoint tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

