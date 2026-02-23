# Guide de Configuration - Système de Sécurité

## Vue d'ensemble

Le système de sécurité existant a été amélioré pour permettre l'activation/désactivation de l'authentification et des permissions via la configuration.

## Configuration

### Variables d'environnement (.env)

```env
# Activer/désactiver l'authentification
AUTHENTICATION_ENABLED=true

# Activer/désactiver les vérifications de permissions
PERMISSION_CHECK_ENABLED=true
```

### Fichier de configuration (app/core/config.py)

```python
class Settings(BaseSettings):
    # Security System
    AUTHENTICATION_ENABLED: bool = True  # Enable/disable authentication
    PERMISSION_CHECK_ENABLED: bool = True  # Enable/disable permission checks
```

## Comportement du système

### Scénario 1: Production (Sécurité complète)
```env
AUTHENTICATION_ENABLED=true
PERMISSION_CHECK_ENABLED=true
```
- ✓ Authentification requise (token JWT)
- ✓ Permissions vérifiées pour chaque action
- ✓ Utilisateurs doivent avoir les permissions appropriées

### Scénario 2: Développement (Sans permissions)
```env
AUTHENTICATION_ENABLED=true
PERMISSION_CHECK_ENABLED=false
```
- ✓ Authentification requise (token JWT)
- ✗ Permissions ignorées (tous les utilisateurs authentifiés ont accès)
- Utile pour tester sans configurer les permissions

### Scénario 3: Tests (Sans sécurité)
```env
AUTHENTICATION_ENABLED=false
PERMISSION_CHECK_ENABLED=false
```
- ✗ Pas d'authentification requise
- ✗ Pas de vérification de permissions
- Un utilisateur mock superuser est créé automatiquement
- Utile pour les tests automatisés

## Modules concernés

### ✓ user_app (app/user_app/routes.py)
- Routes d'authentification: `/auth/*`
- Routes de gestion: `/services`, `/groups`, `/employees`, `/users`, etc.
- Utilise: `get_current_user` (configurable)

### ✓ paie_app (app/paie_app/routes.py)
- Routes de paie: `/alerts`, `/retenues`, `/periodes`, `/entrees`
- Routes d'export: `/payroll/export/*`
- Routes de statistiques: `/statistics/*`
- Utilise: `require_permission(resource, action)` (configurable)

### ✓ audit_app (app/audit_app/routes.py)
- Routes d'audit: `/audit-logs/*`
- Utilise: `require_permission("audit", "view")` (configurable)

## Fonctions modifiées

### 1. get_current_user (app/core/security.py)
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(lambda: None)
):
    """
    - Si AUTHENTICATION_ENABLED=False: Retourne un utilisateur mock superuser
    - Si AUTHENTICATION_ENABLED=True: Valide le token et retourne l'utilisateur
    """
```

### 2. require_permission (app/core/permissions.py)
```python
def require_permission(resource: str, action: str):
    """
    - Si AUTHENTICATION_ENABLED=False: Retourne un utilisateur mock superuser
    - Si PERMISSION_CHECK_ENABLED=False: Retourne l'utilisateur sans vérifier les permissions
    - Si les deux sont activés: Vérifie les permissions normalement
    """
```

### 3. check_permission_or_403 (app/core/permissions.py)
```python
async def check_permission_or_403(
    db: AsyncSession,
    user: User,
    resource: str,
    action: str
):
    """
    - Si AUTHENTICATION_ENABLED=False ou PERMISSION_CHECK_ENABLED=False: Passe toujours
    - Sinon: Vérifie les permissions et lève une exception 403 si refusé
    """
```

## Utilisateur Mock

Quand l'authentification est désactivée, un utilisateur mock est créé:

```python
User(
    id=0,
    email="system@localhost",
    nom="System",
    prenom="User",
    is_active=True,
    is_superuser=True  # Bypass toutes les permissions
)
```

## Exemples d'utilisation

### Route avec authentification simple
```python
@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    # Fonctionne selon AUTHENTICATION_ENABLED
    return {"user_id": current_user.id}
```

### Route avec permission
```python
@router.post("/employees")
async def create_employee(
    employee: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("employe", "CREATE"))
):
    # Fonctionne selon AUTHENTICATION_ENABLED et PERMISSION_CHECK_ENABLED
    pass
```

### Vérification inline
```python
async def delete_employee(employee_id: int, db: AsyncSession, user: User):
    # Vérifier la permission avant de supprimer
    await check_permission_or_403(db, user, "employe", "DELETE")
    # Procéder avec la suppression
```

## Tests

### Test sans authentification
```python
import os
os.environ["AUTHENTICATION_ENABLED"] = "false"

# Les routes fonctionnent sans token
response = client.get("/employees")
assert response.status_code == 200
```

### Test avec authentification
```python
os.environ["AUTHENTICATION_ENABLED"] = "true"

# Token requis
headers = {"Authorization": f"Bearer {access_token}"}
response = client.get("/employees", headers=headers)
assert response.status_code == 200
```

## Permissions par module

### user_app
- `service`: READ, CREATE, UPDATE, DELETE
- `group`: READ, CREATE, UPDATE, DELETE
- `employe`: READ, CREATE, UPDATE, DELETE
- `user`: READ, CREATE, UPDATE, DELETE
- `permission`: READ, CREATE
- `contrat`: READ, CREATE, UPDATE, DELETE
- `document`: READ, CREATE, UPDATE, DELETE

### paie_app
- `alert`: view, create, update
- `retenue`: view, create
- `periode`: view, create, update
- `entree`: view, update
- `payroll`: view
- `payslip`: CREATE

### audit_app
- `audit`: view

## Vérification

Pour vérifier que la configuration fonctionne:

```python
from app.core.config import settings

print(f"Authentication: {settings.AUTHENTICATION_ENABLED}")
print(f"Permissions: {settings.PERMISSION_CHECK_ENABLED}")
```

## Notes importantes

1. **Superusers**: Les utilisateurs avec `is_superuser=True` bypass toujours les permissions
2. **Routes publiques**: Les routes sans dépendance de sécurité restent publiques
3. **Audit**: Le système d'audit continue de fonctionner normalement
4. **Production**: Toujours utiliser `AUTHENTICATION_ENABLED=true` et `PERMISSION_CHECK_ENABLED=true` en production

## Résumé des modifications

✓ `app/core/config.py`: Ajout de `AUTHENTICATION_ENABLED` et `PERMISSION_CHECK_ENABLED`
✓ `app/core/security.py`: `get_current_user` respecte la configuration
✓ `app/core/permissions.py`: `require_permission` et `check_permission_or_403` respectent la configuration
✓ Aucune modification des routes nécessaire (système existant amélioré)
