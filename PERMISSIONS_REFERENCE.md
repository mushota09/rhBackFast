# Référence des Permissions par Module

## Vue d'ensemble

Ce document liste toutes les permissions utilisées dans les modules `user_app`, `paie_app` et `audit_app`.

## Format

```
Resource: action
```

## Module: user_app

### Routes actuellement protégées

La plupart des routes de `user_app` utilisent uniquement `get_current_user` (authentification sans permission).

**Recommandation:** Ajouter des permissions pour une sécurité renforcée.

### Permissions suggérées

```
service: READ, CREATE, UPDATE, DELETE
group: READ, CREATE, UPDATE, DELETE
employe: READ, CREATE, UPDATE, DELETE, EXPORT
user: READ, CREATE, UPDATE, DELETE
permission: READ, CREATE
group_permission: READ, CREATE, UPDATE, DELETE
user_group: READ, CREATE, UPDATE, DELETE
contrat: READ, CREATE, UPDATE, DELETE
document: READ, CREATE, UPDATE, DELETE
```

### Exemple d'implémentation

```python
# Avant (authentification seulement)
@router.get("/employees")
async def list_employees(
    current_user: User = Depends(get_current_user)
):
    pass

# Après (avec permission)
@router.get("/employees")
async def list_employees(
    current_user: User = Depends(require_permission("employe", "READ"))
):
    pass
```

## Module: paie_app

### Permissions actuelles

```
alert: view, create, update
retenue: view, create
periode: view, create, update
entree: view, update
payroll: view
payslip: CREATE
statistics: READ
```

### Détail par route

#### Alerts
- `GET /alerts` → `require_permission("alert", "view")`
- `POST /alerts` → `require_permission("alert", "create")`
- `GET /alerts/{id}` → `require_permission("alert", "view")`
- `POST /alerts/{id}/send-notification` → `require_permission("alert", "update")`

#### Retenues
- `GET /retenues` → `require_permission("retenue", "view")`
- `POST /retenues` → `require_permission("retenue", "create")`

#### Periodes
- `GET /periodes` → `require_permission("periode", "view")`
- `POST /periodes` → `require_permission("periode", "create")`
- `POST /periodes/{id}/process` → `require_permission("periode", "update")`
- `POST /periodes/{id}/finalize` → `require_permission("periode", "update")`
- `POST /periodes/{id}/approve` → `require_permission("periode", "update")`

#### Entrees
- `GET /entrees` → `require_permission("entree", "view")`
- `POST /entrees/{id}/calculate` → `require_permission("entree", "update")`

#### Payroll
- `GET /payroll/export/*` → `require_permission("payroll", "view")`
- `POST /payroll/entrees/{id}/generate-payslip` → `require_permission("entree", "view")`
- `GET /payroll/entrees/{id}/download-payslip` → `require_permission("entree", "view")`
- `POST /payroll/periodes/{id}/generate-all-payslips` → `require_permission("periode", "view")`

#### Statistics
- `GET /statistics/*` → `require_permission("payroll", "view")` ou `require_permission("retenue", "view")` ou `require_permission("alert", "view")`

#### History
- `GET /history/entrees/{id}` → `require_permission("entree", "view")`
- `GET /history/retenues/{id}` → `require_permission("retenue", "view")`

### Recommandation

Standardiser les actions: utiliser `READ` au lieu de `view`, `CREATE` au lieu de `create`, etc.

```python
# Avant
require_permission("alert", "view")

# Après (standardisé)
require_permission("alert", "READ")
```

## Module: audit_app

### Permissions actuelles

```
audit: view
```

### Détail par route

- `GET /audit-logs` → `require_permission("audit", "view")`
- `GET /audit-logs/stats` → `require_permission("audit", "view")`
- `GET /audit-logs/users/{id}` → `require_permission("audit", "view")`
- `GET /audit-logs/resources/{type}` → `require_permission("audit", "view")`
- `GET /audit-logs/{id}` → `require_permission("audit", "view")`

### Recommandation

Standardiser l'action: utiliser `READ` au lieu de `view`.

```python
# Avant
require_permission("audit", "view")

# Après (standardisé)
require_permission("audit", "READ")
```

## Actions Standard Recommandées

Pour une cohérence dans tout le système:

```
READ    - Lire/consulter une ressource
CREATE  - Créer une nouvelle ressource
UPDATE  - Modifier une ressource existante
DELETE  - Supprimer une ressource
EXPORT  - Exporter des données
APPROVE - Approuver une action (workflow)
```

## Création des Permissions

### Automatique (AUTO_CREATE_PERMISSIONS=True)

Les permissions sont créées automatiquement au démarrage de l'application.

### Manuel (Production)

```python
# Créer une permission via l'API
POST /permissions
{
    "resource": "employe",
    "action": "READ",
    "description": "Lire les informations des employés"
}
```

### Via Script

```python
# create_permissions.py
from app.user_app.models import Permission

permissions = [
    {"resource": "employe", "action": "READ"},
    {"resource": "employe", "action": "CREATE"},
    {"resource": "employe", "action": "UPDATE"},
    {"resource": "employe", "action": "DELETE"},
]

for perm in permissions:
    db.add(Permission(**perm))
db.commit()
```

## Attribution des Permissions

### Via Groupes (Recommandé)

```python
# Créer un groupe
POST /groups
{
    "code": "RH_MANAGER",
    "nom": "Gestionnaire RH"
}

# Attribuer des permissions au groupe
POST /group-permissions
{
    "group_id": 1,
    "permission_id": 1,
    "granted": true
}

# Ajouter un utilisateur au groupe
POST /user-groups
{
    "user_id": 1,
    "group_id": 1
}
```

### Vérification

```python
# Vérifier les permissions d'un utilisateur
GET /group-permissions/users/{user_id}/permissions

# Réponse
{
    "user_id": 1,
    "permissions": [
        {"resource": "employe", "action": "READ", "granted": true},
        {"resource": "employe", "action": "CREATE", "granted": true}
    ]
}
```

## Superusers

Les utilisateurs avec `is_superuser=True` bypass toutes les vérifications de permissions.

```python
# Créer un superuser
POST /users
{
    "email": "admin@example.com",
    "password": "secure_password",
    "is_superuser": true
}
```

## Configuration des Permissions

### Activer les vérifications

```env
AUTHENTICATION_ENABLED=true
PERMISSION_CHECK_ENABLED=true
```

### Désactiver les vérifications (développement)

```env
AUTHENTICATION_ENABLED=true
PERMISSION_CHECK_ENABLED=false
```

Avec cette configuration, tous les utilisateurs authentifiés ont accès à toutes les routes.

## Matrice de Permissions Recommandée

### Rôle: Administrateur
```
Toutes les permissions (is_superuser=true)
```

### Rôle: Gestionnaire RH
```
employe: READ, CREATE, UPDATE
user: READ, CREATE
contrat: READ, CREATE, UPDATE
document: READ, CREATE, UPDATE
group: READ
```

### Rôle: Gestionnaire Paie
```
periode: READ, CREATE, UPDATE, APPROVE
entree: READ, UPDATE
retenue: READ, CREATE
payroll: READ, EXPORT
alert: READ, UPDATE
```

### Rôle: Auditeur
```
audit: READ
employe: READ
periode: READ
entree: READ
```

### Rôle: Employé
```
employe: READ (seulement ses propres données)
document: READ (seulement ses propres documents)
entree: READ (seulement ses propres fiches de paie)
```

## Exemple Complet

```python
# 1. Créer les permissions
permissions = [
    Permission(resource="employe", action="READ"),
    Permission(resource="employe", action="CREATE"),
]

# 2. Créer un groupe
group = Group(code="RH_STAFF", nom="Personnel RH")

# 3. Attribuer les permissions au groupe
for perm in permissions:
    GroupPermission(
        group_id=group.id,
        permission_id=perm.id,
        granted=True
    )

# 4. Ajouter un utilisateur au groupe
UserGroup(user_id=user.id, group_id=group.id)

# 5. L'utilisateur peut maintenant accéder aux routes protégées
@router.get("/employees")
async def list_employees(
    current_user: User = Depends(require_permission("employe", "READ"))
):
    # L'utilisateur a la permission, la route s'exécute
    pass
```

## Dépannage

### Erreur 403: Permission denied

```
Vérifier:
1. L'utilisateur est-il dans un groupe?
2. Le groupe a-t-il la permission?
3. La permission est-elle granted=true?
4. PERMISSION_CHECK_ENABLED est-il à true?
```

### Erreur 401: Authentication required

```
Vérifier:
1. Le token JWT est-il valide?
2. Le token est-il expiré?
3. AUTHENTICATION_ENABLED est-il à true?
```

### Bypass temporaire

```env
# Pour le développement uniquement
PERMISSION_CHECK_ENABLED=false
```

## Ressources

- Guide de configuration: `SECURITY_CONFIG_GUIDE.md`
- Résumé d'implémentation: `IMPLEMENTATION_SUMMARY.md`
- Script de test: `test_security_config.py`
