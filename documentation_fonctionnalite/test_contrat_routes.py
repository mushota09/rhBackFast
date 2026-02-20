"""Test script to verify contrat routes are properly configured"""
import ast
import sys


def check_contrat_routes():
    """Check if contrat routes are properly configured"""
    print("Checking Contrat Routes Configuration...")
    print("=" * 50)

    # Read the routes file
    with open("app/user_app/routes.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Parse the AST
    try:
        tree = ast.parse(content)
        print("✓ File parses successfully (no syntax errors)")
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False

    # Check for contrat_router
    has_router = "contrat_router = APIRouter" in content
    print(f"{'✓' if has_router else '✗'} contrat_router defined")

    # Check for required routes
    routes = {
        "GET /contracts (list)": '@contrat_router.get("/")',
        "POST /contracts": '@contrat_router.post(',
        "GET /contracts/{id}": '@contrat_router.get("/{contract_id}"',
        "PUT /contracts/{id}": '@contrat_router.put("/{contract_id}"',
        "DELETE /contracts/{id}": '@contrat_router.delete("/{contract_id}"'
    }

    all_routes_present = True
    for route_name, route_pattern in routes.items():
        present = route_pattern in content
        print(f"{'✓' if present else '✗'} {route_name}")
        if not present:
            all_routes_present = False

    # Check for pagination support
    has_pagination = all([
        "skip: int = 0" in content,
        "limit: int = 100" in content,
        "no_pagination: bool" in content,
        '"skip": skip' in content,
        '"limit": limit' in content
    ])
    print(f"{'✓' if has_pagination else '✗'} Pagination support")

    # Check for expand support
    has_expand = all([
        "expand: Optional[str]" in content,
        "parse_expand_param" in content,
        "apply_expansion" in content
    ])
    print(f"{'✓' if has_expand else '✗'} Expand support")

    # Check for filter support
    has_filters = all([
        "employe_id: Optional[int]" in content,
        "is_active: Optional[bool]" in content
    ])
    print(f"{'✓' if has_filters else '✗'} Filter support (employe_id, is_active)")

    print("=" * 50)

    if all([has_router, all_routes_present, has_pagination, has_expand, has_filters]):
        print("SUCCESS: All Contrat routes are properly configured!")
        return True
    else:
        print("FAILURE: Some routes or features are missing")
        return False


if __name__ == "__main__":
    success = check_contrat_routes()
    sys.exit(0 if success else 1)

