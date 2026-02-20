# Exemple de Réponse : Permissions d'un Utilisateur

## 📋 Requête

```http
GET /api/group-permissions/users/5/permissions
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## ✅ Réponse Complète (200 OK)

```json
{
  "groups": [
    {
      "id": 2,
      "code": "RRH",
      "name": "Ressources Humaines",
      "description": "Gestion complète des ressources humaines",
      "assigned_at": "2024-01-15T10:30:00"
    },
    {
      "id": 5,
      "code": "MANAGER",
      "name": "Managers",
      "description": "Responsables d'équipe avec permissions de gestion",
      "assigned_at": "2024-02-01T14:20:00"
    }
  ],
  "permissions": [
    {
      "id": 1,
      "codename": "employee.READ",
      "name": "Voir les employés",
      "resource": "employee",
      "action": "READ",
      "description": "Permission de lecture des informations des employés",
      "granted_by_group": "RRH"
    },
    {
      "id": 2,
      "codename": "employee.CREATE",
      "name": "Créer des employés",
      "resource": "employee",
      "action": "CREATE",
      "description": "Permission de création de nouveaux employés",
      "granted_by_group": "RRH"
    },
    {
      "id": 3,
      "codename": "employee.UPDATE",
      "name": "Modifier les employés",
      "resource": "employee",
      "action": "UPDATE",
      "description": "Permission de modification des informations des employés",
      "granted_by_group": "RRH"
    },
    {
      "id": 4,
      "codename": "employee.DELETE",
      "name": "Supprimer des employés",
      "resource": "employee",
      "action": "DELETE",
      "description": "Permission de suppression d'employés",
      "granted_by_group": "RRH"
    },
    {
      "id": 10,
      "codename": "contract.READ",
      "name": "Voir les contrats",
      "resource": "contract",
      "action": "READ",
      "description": "Permission de lecture des contrats de travail",
      "granted_by_group": "RRH"
    },
    {
      "id": 11,
      "codename": "contract.CREATE",
      "name": "Créer des contrats",
      "resource": "contract",
      "action": "CREATE",
      "description": "Permission de création de contrats de travail",
      "granted_by_group": "RRH"
    },
    {
      "id": 20,
      "codename": "leave.READ",
      "name": "Voir les demandes de congé",
      "resource": "leave",
      "action": "READ",
      "description": "Permission de lecture des demandes de congé",
      "granted_by_group": "MANAGER"
    },
    {
      "id": 21,
      "codename": "leave.APPROVE",
      "name": "Approuver les congés",
      "resource": "leave",
      "action": "APPROVE",
      "description": "Permission d'approbation des demandes de congé",
      "granted_by_group": "MANAGER"
    },
    {
      "id": 22,
      "codename": "leave.REJECT",
      "name": "Rejeter les congés",
      "resource": "leave",
      "action": "REJECT",
      "description": "Permission de rejet des demandes de congé",
      "granted_by_group": "MANAGER"
    },
    {
      "id": 30,
      "codename": "payroll.READ",
      "name": "Voir la paie",
      "resource": "payroll",
      "action": "READ",
      "description": "Permission de lecture des informations de paie",
      "granted_by_group": "RRH"
    },
    {
      "id": 40,
      "codename": "document.READ",
      "name": "Voir les documents",
      "resource": "document",
      "action": "READ",
      "description": "Permission de lecture des documents des employés",
      "granted_by_group": "RRH"
    },
    {
      "id": 41,
      "codename": "document.CREATE",
      "name": "Créer des documents",
      "resource": "document",
      "action": "CREATE",
      "description": "Permission de création de documents",
      "granted_by_group": "RRH"
    }
  ],
  "total_groups": 2,
  "total_permissions": 12
}
```

---

## 📊 Analyse de la Réponse

### Groupes (2)

| ID | Code | Nom | Assigné le |
|----|------|-----|------------|
| 2 | RRH | Ressources Humaines | 15/01/2024 |
| 5 | MANAGER | Managers | 01/02/2024 |

### Permissions par Groupe

#### Groupe RRH (9 permissions)
- ✅ `employee.READ` - Voir les employés
- ✅ `employee.CREATE` - Créer des employés
- ✅ `employee.UPDATE` - Modifier les employés
- ✅ `employee.DELETE` - Supprimer des employés
- ✅ `contract.READ` - Voir les contrats
- ✅ `contract.CREATE` - Créer des contrats
- ✅ `payroll.READ` - Voir la paie
- ✅ `document.READ` - Voir les documents
- ✅ `document.CREATE` - Créer des documents

#### Groupe MANAGER (3 permissions)
- ✅ `leave.READ` - Voir les demandes de congé
- ✅ `leave.APPROVE` - Approuver les congés
- ✅ `leave.REJECT` - Rejeter les congés

### Permissions par Resource

| Resource | Actions Disponibles |
|----------|---------------------|
| **employee** | READ, CREATE, UPDATE, DELETE |
| **
umaines (RRH) - depuis le 15/01/2024       │
│   • Managers (MANAGER) - depuis le 01/02/2024              │
│                                                             │
│ 🔐 Permissions (12)                                         │
│                                                             │
│ Employés                                                    │
│   ✓ Voir les employés                          [RRH]       │
│   ✓ Créer des employés                         [RRH]       │
│   ✓ Modifier les employés                      [RRH]       │
│   ✓ Supprimer des employés                     [RRH]       │
│                                                             │
│ Contrats                                                    │
│   ✓ Voir les contrats
                 [RRH]       │
│   ✓ Créer des contrats                         [RRH]       │
│                                                             │
│ Congés                                                      │
│   ✓ Voir les demandes de congé                 [MANAGER]   │
│   ✓ Approuver les congés                       [MANAGER]   │
│   ✓ Rejeter les congés                         [MANAGER]   │
│                                                             │
│ Paie                                                        │
│   ✓ Voir la paie                                [RRH
]       │
│                                                             │
│ Documents                                                   │
│   ✓ Voir les documents                          [RRH]       │
│   ✓ Créer des documents                         [RRH]       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Code pour Parser la Réponse

### JavaScript/TypeScript

```typescript
interface Permission {
  id: number;
  codename: string;
  name: string;
  resource: string;
  action: string;
  description: string;
  granted_by_group: string;
}

interface Group {
  id: number;
  code: string;
  name: string;
  description: string;
  assigned_at: string;
}

interface UserPermissionsResponse {
  groups: Group[];
  permissions: Permission[];
  total_groups: number;
  total_permissions: number;
}

// Parser la réponse
function parsePermissions(data: UserPermissionsResponse) {
  // Organiser par resource
  const byResource: Record<string, Permission[]> = {};

  data.permissions.forEach(perm => {
    if (!byResource[perm.resource]) {
      byResource[perm.resource] = [];
    }
    byResource[perm.resource].push(perm);
  });

  return {
    groups: data.groups,
    byResource,
    total: data.total_p
ermissions
  };
}

// Vérifier une permission
function hasPermission(
  data: UserPermissionsResponse,
  resource: string,
  action: string
): boolean {
  const codename = `${resource}.${action}`;
  return data.permissions.some(p => p.codename === codename);
}

// Utilisation
const response = await fetch('/api/group-permissions/users/5/permissions');
const data: UserPermissionsResponse = await response.json();

const parsed = parsePermissions(data);
console.log('Permissions par resource:', parsed.byResource);
rce].append(perm)

    return by_resource

def has_permission(data: Dict[str, Any], resource: str, action: str) -> bool:
    """Vérifier si l'utilisateur a une permission"""
    codename = f"{resource}.{action}"
    return any(p['codename'] == codename for p in data['permissions'])

# Utilisation
import requests

response = requests.get(
    'http://localhost:8000/api/group-permissions/users/5/permissions',
    headers={'Authorization': f'Bearer {token}'}
)
data = response.json()

by_resource = parse_permissions(data)
print(f"Resources: {list(by_resource.keys())}")

can_create = has_permission(data, 'employee', 'CREATE')
print(f"Peut créer des employés: {can_create}")
```

---

## 🔍 Cas Particuliers

### Utilisateur sans Permissions

**Requête :**
```http
GET /api/group-permissions/users/10/permissions
```

**Réponse :**
```json
{
  "groups": [],
  "permissions": [],
  "total_groups": 0,
  "total_permissions": 0
}
```

### Utilisateur avec un Seul Groupe

**Réponse :**
```json
{
  "groups": [
    {
      "id": 3,
      "code": "VIEWER",
      "name": "Lecteurs",
      "description": "Accès en lecture seule",
      "assigned_at": "2024-02-10T09:00:00"
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
      "granted_by_group": "VIEWER"
    }
  ],
  "total_groups": 1,
  "total_permissions": 1
}
```

### Superutilisateur

Les superutilisateurs ont **toutes** les permissions, même s'ils ne sont dans aucun groupe.

**Note :** L'endpoint retourne les permissions explicites via les groupes. Pour les superutilisateurs, vérifiez le champ `is_superuser` de l'utilisateur.

---

## 🎯 Résumé

### URL
```
GET /api/group-permissions/users/{user_id}/permissions
```

### Structure de la Réponse
```json
{
  "groups": [...],           // Groupes de l'utilisateur
  "permissions": [...],      // Toutes les permissions
  "total_groups": number,    // Nombre de groupes
  "total_permissions": number // Nombre de permissions
}
```

### Champs Importants

**Permission :**
- `codename` : Identifiant unique (ex: "employee.CREATE")
- `resource` : Resource concernée (ex: "employee")
- `action` : Action autorisée (ex: "CREATE")
- `granted_by_group` : Groupe qui donne cette permission

**Group :**
- `code` : Code court du groupe (ex: "RRH")
- `name` : Nom complet du groupe
- `assigned_at` : Date d'assignation

---

## 📖 Voir Aussi

- [Guide Complet des Permissions](./GUIDE_PERMISSIONS_UTILISATEUR.md)
- [Guide des Expansions](./GUIDE_EXPAND_RELATIONS.md)
- [Documentation de l'API](./API_ENDPOINTS_COMPLETE.md)
