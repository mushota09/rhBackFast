# Implémentation des Opérations Bulk - RBAC

## Vue d'ensemble

Ce document décrit l'implémentation de trois nouveaux endpoints pour les opérations en masse (bulk) dans le système RBAC de rhBackFast.

**Date d'implémentation**: 2026-02-26  
**Version**: 1.0.0  
**Auteur**: Système d'IA Kiro

---

## Endpoints Implémentés

### 1. Bulk Assign Users to Groups

**Endpoint**: `POST /api/user-groups/bulk-assign/`  
**Authentification**: Requise  
**Status Code**: 201 Created

#### Description
Permet d'assigner plusieurs utilisateurs à plusieurs groupes en une seule opération.

#### Request Body
```json
{
  "user_ids": [1, 2, 3],
  "group_ids": [1, 2],
  "is_active": true,
  "replace_existing": false
}
```

#### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| user_ids | List[int] | Oui | Liste des IDs d'utilisateurs à assigner |
| group_ids | List[int] | Oui | Liste des IDs de groupes |
| is_active | bool | Non | Si les assignations doivent être actives (défaut: true) |
| replace_existing | bool | Non | Si true, supprime les assignations existantes avant d'ajouter les nouvelles (défaut: false) |

#### Response
```json
{
  "success": true,
  "message": "Successfully processed 6 assignments",
  "created_count": 4,
  "updated_count": 2,
  "deleted_count": 0,
  "failed_count": 0,
  "errors": []
}
```

#### Comportement

1. **Validation**: Vérifie que tous les utilisateurs et groupes existent
2. **Replace Existing**: Si `replace_existing=true`, supprime d'abord toutes les assignations existantes pour ces utilisateurs
3. **Création/Mise à jour**: 
   - Si l'assignation existe déjà, met à jour le statut `is_active`
   - Sinon, crée une nouvelle assignation
4. **Gestion d'erreurs**: Continue le traitement même si certaines opérations échouent, retourne les erreurs dans la réponse

#### Exemple d'utilisation

```python
import requests

token = "your_access_token"
headers = {"Authorization": f"Bearer {token}"}

data = {
    "user_ids": [1, 2, 3],
    "group_ids": [1, 2],
    "is_active": True,
    "replace_existing": False
}

response = requests.post(
    "http://localhost:8000/api/user-groups/bulk-assign/",
    headers=headers,
    json=data
)

print(response.json())
```

#### Cas d'usage

- Assigner un nouveau groupe à tous les employés d'un service
- Migrer des utilisateurs d'un groupe à un autre (avec `replace_existing=true`)
- Activer/désactiver en masse des assignations

---

### 2. Bulk Remove Users from Groups

**Endpoint**: `POST /api/user-groups/bulk-remove/`  
**Authentification**: Requise  
**Status Code**: 200 OK

#### Description
Permet de retirer plusieurs utilisateurs de plusieurs groupes en une seule opération.

#### Request Body
```json
{
  "user_ids": [1, 2, 3],
  "group_ids": [1, 2]
}
```

#### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| user_ids | List[int] | Oui | Liste des IDs d'utilisateurs |
| group_ids | List[int] | Oui | Liste des IDs de groupes à retirer |

#### Response
```json
{
  "success": true,
  "message": "Successfully removed 6 assignments",
  "created_count": 0,
  "updated_count": 0,
  "deleted_count": 6,
  "failed_count": 0,
  "errors": []
}
```

#### Comportement

1. **Recherche**: Pour chaque combinaison utilisateur-groupe, recherche l'assignation
2. **Suppression**: Si l'assignation existe, la supprime
3. **Gestion d'erreurs**: Si l'assignation n'existe pas, ajoute un message d'erreur mais continue le traitement

#### Exemple d'utilisation

```python
import requests

token = "your_access_token"
headers = {"Authorization": f"Bearer {token}"}

data = {
    "user_ids": [1, 2, 3],
    "group_ids": [1, 2]
}

response = requests.post(
    "http://localhost:8000/api/user-groups/bulk-remove/",
    headers=headers,
    json=data
)

print(response.json())
```

#### Cas d'usage

- Retirer tous les employés d'un service d'un groupe temporaire
- Nettoyer les assignations obsolètes
- Révoquer l'accès à plusieurs utilisateurs simultanément

---

### 3. Bulk Update Group Permissions

**Endpoint**: `POST /api/group-permissions/bulk-update/{group_id}/`  
**Authentification**: Requise  
**Status Code**: 200 OK

#### Description
Permet de mettre à jour plusieurs permissions pour un groupe en une seule opération.

#### Request Body
```json
{
  "permissions": [
    {"permission_id": 1, "granted": true},
    {"permission_id": 2, "granted": false},
    {"permission_id": 3, "granted": true}
  ]
}
```

#### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| group_id | int | Oui | ID du groupe (dans l'URL) |
| permissions | List[dict] | Oui | Liste des mises à jour de permissions |
| permissions[].permission_id | int | Oui | ID de la permission |
| permissions[].granted | bool | Non | Si la permission est accordée (défaut: true) |

#### Response
```json
{
  "success": true,
  "message": "Successfully processed 3 permissions",
  "created_count": 1,
  "updated_count": 2,
  "deleted_count": 0,
  "failed_count": 0,
  "errors": []
}
```

#### Comportement

1. **Validation**: Vérifie que le groupe existe
2. **Validation des permissions**: Pour chaque permission, vérifie qu'elle existe
3. **Création/Mise à jour**:
   - Si la permission de groupe existe déjà, met à jour le statut `granted`
   - Sinon, crée une nouvelle permission de groupe
4. **Gestion d'erreurs**: Continue le traitement même si certaines opérations échouent

#### Exemple d'utilisation

```python
import requests

token = "your_access_token"
headers = {"Authorization": f"Bearer {token}"}

group_id = 1
data = {
    "permissions": [
        {"permission_id": 1, "granted": True},
        {"permission_id": 2, "granted": False},
        {"permission_id": 3, "granted": True}
    ]
}

response = requests.post(
    f"http://localhost:8000/api/group-permissions/bulk-update/{group_id}/",
    headers=headers,
    json=data
)

print(response.json())
```

#### Cas d'usage

- Configurer rapidement toutes les permissions d'un nouveau groupe
- Mettre à jour les permissions d'un groupe suite à un changement de politique
- Synchroniser les permissions entre environnements

---

## Schémas Pydantic

### BulkUserGroupAssign
```python
class BulkUserGroupAssign(BaseModel):
    user_ids: List[int] = Field(..., min_length=1)
    group_ids: List[int] = Field(..., min_length=1)
    is_active: bool = Field(default=True)
    replace_existing: bool = Field(default=False)
```

### BulkUserGroupRemove
```python
class BulkUserGroupRemove(BaseModel):
    user_ids: List[int] = Field(..., min_length=1)
    group_ids: List[int] = Field(..., min_length=1)
```

### BulkGroupPermissionUpdate
```python
class BulkGroupPermissionUpdate(BaseModel):
    permissions: List[dict] = Field(..., min_length=1)
```

### BulkOperationResponse
```python
class BulkOperationResponse(BaseModel):
    success: bool
    message: str
    created_count: int = 0
    updated_count: int = 0
    deleted_count: int = 0
    failed_count: int = 0
    errors: List[str] = []
```

---

## Gestion des Erreurs

### Erreurs de Validation

Si des utilisateurs, groupes ou permissions n'existent pas, l'opération continue mais retourne les erreurs:

```json
{
  "success": false,
  "message": "Validation failed",
  "created_count": 0,
  "updated_count": 0,
  "deleted_count": 0,
  "failed_count": 2,
  "errors": [
    "User with ID 999 not found",
    "Group with ID 888 not found"
  ]
}
```

### Erreurs Système

En cas d'erreur système, l'opération est annulée (rollback) et retourne une erreur HTTP 500:

```json
{
  "detail": "Bulk assignment failed: Database connection error"
}
```

---

## Tests

Un script de test complet est disponible dans `test_bulk_operations.py`.

### Exécution des tests

```bash
# Démarrer le serveur FastAPI
uvicorn main:app --reload

# Dans un autre terminal, exécuter les tests
python test_bulk_operations.py
```

### Tests inclus

1. ✅ Bulk assign users to groups
2. ✅ Bulk update group permissions
3. ✅ Bulk remove users from groups
4. ✅ Validation error handling

---

## Performance

### Optimisations

- **Validation en amont**: Tous les utilisateurs et groupes sont validés avant de commencer les opérations
- **Transactions**: Toutes les opérations sont effectuées dans une seule transaction
- **Rollback automatique**: En cas d'erreur système, toutes les modifications sont annulées

### Limites Recommandées

Pour des performances optimales:

- **user_ids**: Maximum 100 utilisateurs par requête
- **group_ids**: Maximum 50 groupes par requête
- **permissions**: Maximum 200 permissions par requête

Pour des opérations plus importantes, divisez-les en plusieurs requêtes.

---

## Sécurité

### Authentification

Tous les endpoints nécessitent un token JWT valide.

### Autorisation

Les endpoints utilisent `get_current_user` pour vérifier l'authentification. Pour ajouter des vérifications de permissions:

```python
@user_group_router.post("/bulk-assign/")
async def bulk_assign_users_to_groups(
    data: schemas.BulkUserGroupAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Vérifier si l'utilisateur a la permission
    has_permission = await check_permission(
        db, current_user.id, "user_group", "CREATE"
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # ... reste du code
```

### Audit

Les opérations bulk peuvent être auditées en ajoutant des logs:

```python
from app.audit_app.services import AuditService

# Après l'opération réussie
await AuditService.log_action(
    db=db,
    user=current_user,
    action="BULK_ASSIGN",
    resource_type="user_group",
    resource_id=f"users:{data.user_ids},groups:{data.group_ids}",
    new_values={"created": created_count, "updated": updated_count},
    request=request
)
```

---

## Migration depuis l'Ancien Système

Si vous avez du code frontend qui utilise les anciennes méthodes individuelles:

### Avant (Ancien code)
```typescript
// Assigner chaque utilisateur individuellement
for (const userId of userIds) {
  for (const groupId of groupIds) {
    await userGroupService.create({
      user_id: userId,
      group_id: groupId,
      is_active: true
    });
  }
}
```

### Après (Nouveau code)
```typescript
// Assigner tous les utilisateurs en une seule requête
await UserManagementApiService.bulkAssignUsersToGroups({
  user_ids: userIds,
  group_ids: groupIds,
  is_active: true,
  replace_existing: false
});
```

---

## Intégration Frontend

Les composants frontend suivants utilisent ces endpoints:

### BulkUserAssignment.tsx
```typescript
const handleSubmit = (values) => {
  bulkAssignUsersToGroups({
    user_ids: values.users,
    group_ids: values.groups,
    is_active: values.is_active,
    replace_existing: values.replace_existing,
  });
};
```

### GroupPermissionMatrix.tsx
```typescript
const handleSave = async () => {
  const permissionUpdates = Array.from(changes.entries()).map(
    ([permissionId, granted]) => ({
      permission_id: permissionId,
      granted,
    })
  );

  await UserManagementApiService.bulkUpdateGroupPermissions(
    selectedGroup.id,
    permissionUpdates
  );
};
```

---

## Dépannage

### Problème: "User with ID X not found"

**Cause**: L'utilisateur n'existe pas dans la base de données  
**Solution**: Vérifiez que tous les IDs d'utilisateurs sont valides

### Problème: "Group with ID X not found"

**Cause**: Le groupe n'existe pas dans la base de données  
**Solution**: Vérifiez que tous les IDs de groupes sont valides

### Problème: "Permission with ID X not found"

**Cause**: La permission n'existe pas dans la base de données  
**Solution**: Vérifiez que tous les IDs de permissions sont valides

### Problème: Timeout sur les grandes opérations

**Cause**: Trop d'opérations en une seule requête  
**Solution**: Divisez l'opération en plusieurs requêtes plus petites

---

## Changelog

### Version 1.0.0 (2026-02-26)

- ✅ Implémentation initiale de `POST /api/user-groups/bulk-assign/`
- ✅ Implémentation initiale de `POST /api/user-groups/bulk-remove/`
- ✅ Implémentation initiale de `POST /api/group-permissions/bulk-update/{group_id}/`
- ✅ Ajout des schémas Pydantic pour les opérations bulk
- ✅ Création du script de test `test_bulk_operations.py`
- ✅ Documentation complète

---

## Références

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

## Support

Pour toute question ou problème concernant ces endpoints, consultez:

1. Cette documentation
2. Le code source dans `app/user_app/routes.py`
3. Les schémas dans `app/user_app/schemas.py`
4. Les tests dans `test_bulk_operations.py`
