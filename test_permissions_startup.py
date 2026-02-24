"""
Script de test pour vérifier les permissions définies dans startup.py
"""

from app.core.startup import CONGE_PERMISSIONS, AUDIT_PERMISSIONS, PAIE_PERMISSIONS


def test_permissions():
    """Affiche toutes les permissions définies"""

    print("\n" + "="*60)
    print("PERMISSIONS DÉFINIES DANS STARTUP.PY")
    print("="*60)

    # Conge app permissions
    print(f"\n📋 CONGE_APP - {len(CONGE_PERMISSIONS)} permissions:")
    print("-" * 60)
    for codename, description in CONGE_PERMISSIONS.items():
        print(f"  • {codename:30} → {description}")

    # Audit app permissions
    print(f"\n📋 AUDIT_APP - {len(AUDIT_PERMISSIONS)} permissions:")
    print("-" * 60)
    for codename, description in AUDIT_PERMISSIONS.items():
        print(f"  • {codename:30} → {description}")

    # Paie app permissions
    print(f"\n📋 PAIE_APP - {len(PAIE_PERMISSIONS)} permissions:")
    print("-" * 60)
    for codename, description in PAIE_PERMISSIONS.items():
        print(f"  • {codename:30} → {description}")

    # Total
    total = len(CONGE_PERMISSIONS) + len(AUDIT_PERMISSIONS) + len(PAIE_PERMISSIONS)
    print(f"\n{'='*60}")
    print(f"TOTAL: {total} permissions spécifiques aux apps")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    test_permissions()
