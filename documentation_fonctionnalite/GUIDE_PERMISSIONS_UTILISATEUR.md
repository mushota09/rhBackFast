# Guide : Récupérer les Permissions d'un Utilisateur

## 🎯 Réponse Rapide

Pour récupérer toutes les permissions d'un utilisateur, utilisez :

```http
GET /api/group-permissions/users/{user_id}/permissions
```

**Exemple :**
```http
GET /api/group-permissions/users/5/permissions
```

---

## 📋 Structure du Système de Permissions

### Architecture RBAC (Role-Based Access Control)

```
User → UserGroup → Group → GroupPermission → Permission
```

**Explication :**
1. Un **User** appartient à un ou plusieurs **Groups** (via UserGroup)
2. Chaque **Group** a des **Permissions** (via GroupPermission)
3. Les permissions d'un utilisateur = somme des permissions de tous ses groupes actifs

---

## 🚀 Utilisation de l'API

### 1. Récupérer les Permissions d'un Utilisateur Spécifique

**Endpoint :**
```http
GET /api/group-permissions/users/{user_id}/permissions
```

**Headers :**
```http
Authorization: Bearer <votre_token_jwt>
```

**Exemple avec cURL :**
```bash
curl -X GET "http://localhost:8000/api/group-permissions/users/5/permissions" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Exemple avec JavaScript :**
```javascript
const response = await fetch('/api/group-permissions/users/5/permissions', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();
console.log(data);
```

**Réponse :**
```json
{
  "groups": [
    {
      "id": 2,
      "code": "RRH",
      "name": "Ressources Humaines",
      "description": "Gestion RH",
      "assigned_at": "2024-01-15T10:30:00"
    },
    {
      "id": 3,
      "code": "MANAGER",
      "name": "Managers",
      "description": "Responsables d'équipe",
      "assigned_at": "2024-01-20T14:00:00"
    }
  ],
  "permissions": [
    {
      "id": 1,
      "codename": "employee.READ",
      "name": "Voir les employés",
      "resource": "employee",
      "action": "READ",
      "description": "Permission de lecture des employés",
      "granted_by_group": "RRH"
    },
    {
      "id": 2,
      "codename": "employee.CREATE",
      "name": "Créer des employés",
      "resource": "employee",
      "action": "CREATE",
      "description": "Permission de création d'employés",
      "granted_by_group": "RRH"
    },
    {
      "id": 5,
      "codename": "leave.APPROVE",
      "name": "Approuver les congés",
      "resource": "leave",
      "action": "APPROVE",
      "description": "Permission d'approbation des congés",
      "granted_by_group": "MANAGER"
    }
  ],
  "total_groups": 2,
  "total_permissions": 3
}
```

---

### 2. Récupérer les Permissions de l'Utilisateur Connecté

Si vous voulez les permissions de l'utilisateur actuellement connecté, vous pouvez :

**Option A : Utiliser l'ID de l'utilisateur connecté**
```javascript
// Après login, vous avez l'ID de l'utilisateur
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password })
});
const { user, access } = await loginResponse.json();

// Récupérer ses permissions
const permissionsResponse = await fetch(`/api/group-permissions/users/${user.id}/permissions`, {
  headers: { 'Authorization': `Bearer ${access}` }
});
```

**Option B : Créer un endpoint dédié (recommandé)**

Si cet endpoint n'existe pas encore, vous pouvez l'ajouter :

```python
# Dans routes.py
@group_permission_router.get(
    "/me/permissions",
    response_model=schemas.UserPermissionsResponse
)
async def get_my_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's effective permissions"""
    permissions_data = await PermissionService.get_effective_permissions(
        db,
        current_user.id
    )
    return permissions_data
```

Puis l'utiliser :
```http
GET /api/group-permissions/me/permissions
```

---

## 🔍 Autres Méthodes pour Récupérer les Permissions

### Méthode 1 : Via l'Expansion (Détails Complets)

Si vous voulez voir les groupes ET leurs permissions en une seule requête :

```http
GET /api/user-groups/?user_id=5&expand=group.group_permissions.permission
```

**Avantages :**
- Récupère tout en une requête
- Montre la structure complète

**Inconvénients :**
- Plus complexe à parser
- Peut contenir des doublons si l'utilisateur a plusieurs groupes

**Réponse :**
```json
{
  "results": [
    {
      "id": 1,
      "user_id": 5,
      "group_id": 2,
      "is_active": true,
      "group": {
        "id": 2,
        "code": "RRH",
        "name": "Ressources Humaines",
        "group_permissions": [
          {
            "id": 1,
            "granted": true,
            "permission": {
              "id": 1,
              "codename": "employee.READ",
              "resource": "employee",
              "action": "READ"
            }
          }
        ]
      }
    }
  ]
}
```

---

### Méthode 2 : Via les User-Groups (Liste des Groupes)

Pour voir simplement les groupes d'un utilisateur :

```http
GET /api/user-groups/?user_id=5&expand=group
```

**Réponse :**
```json
{
  "results": [
    {
      "id": 1,
      "user_id": 5,
      "group_id": 2,
      "is_active": true,
      "group": {
        "id": 2,
        "code": "RRH",
        "name": "Ressources Humaines"
      }
    }
  ]
}
```

---

### Méthode 3 : Via les Group-Permissions (Permissions d'un Groupe)

Pour voir les permissions d'un groupe spécifique :

```http
GET /api/group-permissions/?group_id=2&expand=permission
```

**Réponse :**
```json
{
  "results": [
    {
      "id": 1,
      "group_id": 2,
      "permission_id": 1,
      "granted": true,
      "permission": {
        "id": 1,
        "codename": "employee.READ",
        "name": "Voir les employés",
        "resource": "employee",
        "action": "READ"
      }
    }
  ]
}
```

---

## 📊 Comparaison des Méthodes

| Méthode | URL | Avantages | Inconvénients |
|---------|-----|-----------|---------------|
| **Endpoint dédié** | `/api/group-permissions/users/{id}/permissions` | ✅ Simple<br>✅ Optimisé<br>✅ Pas de doublons | ❌ Endpoint spécifique |
| **Expansion complète** | `/api/user-groups/?user_id={id}&expand=...` | ✅ Flexible<br>✅ Structure complète | ❌ Complexe à parser<br>❌ Peut avoir des doublons |
| **Par groupe** | `/api/user-groups/?user_id={id}` puis `/api/group-permissions/?group_id={id}` | ✅ Contrôle total | ❌ Plusieurs requêtes<br>❌ Plus lent |

**Recommandation : Utilisez l'endpoint dédié** `/api/group-permissions/users/{user_id}/permissions`

---

## 💡 Cas d'Usage Pratiques

### Cas 1 : Afficher les Permissions dans un Profil Utilisateur

```javascript
async function loadUserProfile(userId) {
  // Récupérer les infos de base
  const userResponse = await fetch(`/api/users/${userId}?expand=employe`);
  const user = await userResponse.json();

  // Récupérer les permissions
  const permissionsResponse = await fetch(
    `/api/group-permissions/users/${userId}/permissions`
  );
  const permissions = await permissionsResponse.json();

  return {
    user,
    permissions
  };
}
```

### Cas 2 : Vérifier si un Utilisateur a une Permission Spécifique

```javascript
async function userHasPermission(userId, resource, action) {
  const response = await fetch(`/api/group-permissions/users/${userId}/permissions`);
  const data = await response.json();

  const permissionCode = `${resource}.${action}`;
  return data.permissions.some(p => p.codename === permissionCode);
}

// Utilisation
const canCreateEmployee = await userHasPermission(5, 'employee', 'CREATE');
if (canCreateEmployee) {
  // Afficher le bouton "Créer un employé"
}
```

### Cas 3 : Afficher les Permissions par Groupe

```javascript
async function getPermissionsByGroup(userId) {
  const response = await fetch(`/a
```jsx
function UserPermissions({ userId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/group-permissions/users/${userId}/permissions`)
      .then(r => r.json())
      .then(setData);
  }, [userId]);

  if (!data) return <div>Chargement...</div>;

  return (
    <div>
      <h2>Groupes ({data.total_groups})</h2>
      <ul>
        {data.groups.map(group => (
          <li key={group.id}>
            <strong>{group.name}</strong> ({group.code})
            <br />
            <small>Assigné le {new Date(group.assigned_at).toLocaleDateString()}</small>
          </li>
        ))}
      </ul>

      <h2>Permissions ({data.total_permissions})</h2>
      <table>
        <thead>
          <tr>
            <th>Nom</th>
            <th>Resource</th>
            <th>Action</th>
            <th>Groupe</th>
          </tr>
        </thead>
        <tbody>
          {data.permissions.map(perm => (
            <tr key={perm.id}>
              <td>{perm.name}</td>
              <td>{perm.resource}</td>
              <td>{perm.action}</td>
              <td>{perm.granted_by_group}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 🔐 Sécurité et Permissions

### Qui Peut Accéder à cet Endpoint ?

L'endpoint `/api/group-permissions/users/{user_id}/permissions` nécessite :
- ✅ Être authentifié (token JWT valide)
- ⚠️ Vérifiez si des permissions spécifiques sont requises

### Bonnes Pratiques

1. **Ne pas exposer les permissions côté client** pour la sécurité
   - Utilisez les permissions côté serveur pour les décisions critiques
   - Côté client, utilisez-les uniquement pour l'UI (afficher/cacher des boutons)

2. **Cacher les permissions sensibles**
   ```javascript
   // ❌ Mauvais
   if (userPermissions.includes('admin.DELETE')) {
     // Permettre la suppression
   }

   // ✅ Bon - Vérifier côté serveur
   try {
     await fetch('/api/admin/delete', { method: 'DELETE' });
   } catch (error) {
     // Le serveur vérifie les permissions
   }
   ```

3. **Mettre en cache les permissions**
   ```javascript
   // Cache les permissions pendant 5 minutes
   const CACHE_DURATION = 5 * 60 * 1000;
   let permissionsCache = null;
   let cacheTime = null;

   async function getUserPermissions(userId) {
     const now = Date.now();
     if (permissionsCache && cacheTime && (now - cacheTime < CACHE_DURATION)) {
       return permissionsCache;
     }

     const response = await fetch(`/api/group-permissions/users/${userId}/permissions`);
     permissionsCache = await response.json();
     cacheTime = now;

     return permissionsCache;
   }
   ```

---

## 🧪 Tests

### Test avec cURL

```bash
# 1. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"mushota09@gmail.com","password":"rapha12345678"}' \
  | jq -r '.access')

# 2. Récupérer les permissions
curl -X GET "http://localhost:8000/api/group-permissions/users/5/permissions" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

### Test avec Python

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login', json={
    'email': 'mushota09@gmail.com',
    'password': 'rapha12345678'
})
token = response.json()['access']

# Récupérer les permissions
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:8000/api/group-permissions/users/5/permissions',
    headers=headers
)
permissions = response.json()

print(f"Groupes: {permissions['total_groups']}")
print(f"Permissions: {permissions['total_permissions']}")
for perm in permissions['permissions']:
    print(f"  - {perm['codename']}: {perm['name']}")
```

---

## 📝 Résumé

### URL Principale
```http
GET /api/group-permissions/users/{user_id}/permissions
```

### Réponse
```json
{
  "groups": [...],           // Liste des groupes de l'utilisateur
  "permissions": [...],      // Liste de toutes les permissions
  "total_groups": 2,         // Nombre de groupes
  "total_permissions": 15    // Nombre de permissions
}
```

### Exemple Complet
```javascript
// Récupérer les permissions
const response = await fetch('/api/group-permissions/users/5/permissions', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Utiliser les permissions
console.log(`L'utilisateur a ${data.total_permissions} permissions`);
console.log(`Réparties dans ${data.total_groups} groupes`);

// Vérifier une permission spécifique
const canEdit = data.permissions.some(p => p.codename === 'employee.UPDATE');
```

---

## 🔗 Ressources Connexes

- [Guide des Expansions](./GUIDE_EXPAND_RELATIONS.md)
- [Documentation de l'API](./API_ENDPOINTS_COMPLETE.md)
- [Système de Permissions](./PERMISSION_SYSTEM_IMPLEMENTATION.md)
