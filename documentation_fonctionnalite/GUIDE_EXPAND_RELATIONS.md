# Guide d'Utilisation des Expand et Back_Populates

## Table des Matières
1. [Introduction](#introduction)
2. [Expand Simple](#expand-simple)
3. [Expand Imbriqué (Nested)](#expand-imbriqué-nested)
4. [Back_Populates](#back_populates)
5. [Exemples Pratiques](#exemples-pratiques)
6. [Bonnes Pratiques](#bonnes-pratiques)

---

## Introduction

Ce guide explique comment utiliser le système d'expansion des relations dans l'API rhBackFast. L'expansion permet de charger automatiquement les objets liés au lieu de recevoir uniquement leurs IDs.

### Concepts Clés

- **Expand Simple** : Charger une relation directe (ex: `user`, `group`)
- **Expand Imbriqué** : Charger des relations à plusieurs niveaux (ex: `user.employe`)
- **Back_Populates** : Configuration SQLAlchemy pour les relations bidirectionnelles

---

## Expand Simple

### Qu'est-ce qu'un Expand Simple ?

Un expand simple charge une relation directe d'un modèle. Au lieu de recevoir un ID, vous recevez l'objet complet.

### Syntaxe

```
GET /api/endpoint/?expand=relation_name
```

### Exemple 1 : User-Groups sans Expand

**Requête :**
```http
GET /api/user-groups/
```

**Réponse :**
```json
{
  "results": [
    {
      "id": 1,
      "user_id": 5,          // ← Juste l'ID
      "group_id": 2,         // ← Juste l'ID
      "is_active": true,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

### Exemple 2 : User-Groups avec Expand User

**Requête :**
```http
GET /api/user-groups/?expand=user
```

**Réponse :**
```json
{
  "results": [
    {
      "id": 1,
      "user_id": 5,
      "user": {
relations en les séparant par des virgules.

**Requête :**
```http
GET /api/user-groups/?expand=user,group
```

**Réponse :**
```json
{
  "results": [
    {
      "id": 1,
      "user_id": 5,
      "user": {              // ← Objet user complet
        "id": 5,
        "email": "john.doe@example.com",
        "nom": "Doe",
        "prenom": "John"
      },
      "group_id": 2,
      "group": {             // ← Objet group complet
        "id": 2,
        "code": "RRH",
        "name": "Ressources Humaines",
        "is_active": true
      },
      "is_active": true
    }
  ],
  "total": 1
}
```

### Endpoints Supportant l'Expand Simple

| Endpoint | Relations Expandables |
|----------|----------------------|
| `/api/user-groups/` | `user`, `group`, `assigned_by_user` |
| `/api/service-groups/` | `service`, `group` |
| `/api/employees/` | `poste`, `user_account`, `responsable` |
| `/api/services/` | `service_groups` |
| `/api/groups/` | `service_groups`, `user_groups` |

---

## Expand Imbriqué (Nested)

### Qu'est-ce qu'un Expand Imbriqué ?

Un expand imbriqué permet de charger des relations à plusieurs niveaux de profondeur. Utilisez la notation point (`.`) pour spécifier le chemin.

### Syntaxe

```
GET /api/endpoint/?expand=parent.child
GET /api/endpoint/?expand=parent.child.grandchild
```

### Exemple 1 : Expand User et son Employé

**Requête :**
```http
GET /api/user-groups/?expand=user.employe
```

**Réponse :**
```json
{
  "results": [
    {
      "id": 1,
      "user_id": 5,
      "user": {
        "id": 5,
        "email": "john.doe@example.com",
        "nom": "Doe",
        "prenom": "John",
        "employe": {         // ← Relation imbriquée !
          "id": 10,
          "matricule": "EMP001",
          "nom": "Doe",
          "prenom": "John",
ce_id": 3,
            "group_id": 2
          },
          {
            "id": 2,
            "service_id": 5,
            "group_id": 2
          }
        ]
      }
    }
  ]
}
```

### Exemple 3 : Expand Multiple Imbriqué

**Requête :**
```http
GET /api/employees/?expand=poste.service,poste.group
```

**Réponse :**
```json
{
  "results": [
    {
      "id": 10,
      "matricule": "EMP001",
      "nom": "Doe",
      "prenom": "John",
      "poste_id": 1,
      "poste": {
        "id": 1,
        "service_id": 3,
        "service": {         // ← Service expandé
          "id": 3,
          "code": "IT",
          "titre": "Informatique"
        },
        "group_id": 2,
        "group": {           // ← Group expandé
          "id": 2,
          "code": "DEV",
          "name": "Développeurs"
        }
      }
    }
  ]
}
```

### Niveaux d'Imbrication Supportés

L'API supporte jusqu'à **3 niveaux d'imbrication** :
- ✅ `user.employe` (2 niveaux)
- ✅ `user.employe.poste` (3 niveaux)
- ❌ `user.employe.poste.service` (4 niveaux - non recommandé)

---

## Back_Populates

### Qu'est-ce que Back_Populates ?

`back_populates` est une configuration SQLAlchemy qui établit une relation **bidirectionnelle** entre deux modèles. Cela permet de naviguer dans les deux sens.

### Pourquoi c'est Important ?

Sans `back_populates`, vous ne pouvez naviguer que dans un sens. Avec `back_populates`, vous pouvez :
- Accéder à `user.employe` (User → Employe)
- Accéder à `employe.user_account` (Employe → User)

### Anatomie d'une Relation avec Back_Populates

#### Modèle User
```python
class User(BaseModel):
    __tablename__ = "user_management_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    employe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relation vers Employe
    employe: Mapped[Optional["Employe"]] = relationship(
        "Employe",
        back_populates="user_account"  # ← Nom de la relation inverse
    )
```

#### Modèle Employe
```python
class Employe(BaseModel):
    __tablename__ = "rh_employe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    matricule: Mapped[str] = mapped_column(String(50))

    # Relation inverse vers User
    user_account: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="employe"  # ← Nom de la relation directe
    )
```

### Règles de Back_Populates

1. **Les noms doivent correspondre** : Le `back_populates` d'un côté doit pointer vers le nom de la relation de l'autre côté
2. **Bidirectionnel** : Les deux modèles doivent avoir la configuration
3. **Cohérence** : Si vous changez un nom, changez-le des deux côtés

### Exemples de Relations avec Back_Populates

#### 1. Relation One-to-Many : Service ↔ ServiceGroup

```python
# Service (One)
class Service(BaseModel):
    service_groups: Mapped[list["ServiceGroup"]] = relationship(
        "ServiceGroup",
        back_populates="service",
        cascade="all, delete-orphan"
    )

# ServiceGroup (Many)
class ServiceGroup(Base):
    service_id: Mapped[int] = mapped_column(ForeignKey("rh_service.id"))

    service: Mapped["Service"] = relationship(
        "Service",
        back_populates="service_groups"
    )
```

**Utilisation :**
```python
# Accès dans les deux sens
service.service_groups  # Liste des ServiceGroups
service_group.service   # Le Service parent
```

#### 2. Relation Many-to-Many : User ↔ Group (via UserGroup)

```python
# User
class User(BaseModel):
    user_groups: Mapped[list["UserGroup"]] = relationship(
        "UserGroup",
        back_populates="user",
        foreign_keys="UserGroup.user_id"
    )

# UserGroup (table d'association)
class UserGroup(BaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("user_management_user.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("user_management_group.id"))

    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_groups",
        foreign_keys=[user_id]
    )
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="user_groups"
    )

# Group
class Group(BaseModel):
    user_groups: Mapped[list["UserGroup"]] = relationship(
        "UserGroup",
        back_populates="group"
    )
```

**Utilisation :**
```python
# Navigation dans tous les sens
user.user_groups        # Liste des UserGroups
user_group.user         # Le User
user_group.group        # Le Group
group.user_groups       # Liste des UserGroups
```

#### 3. Relation Self-Referential : User ↔ UserGroup (assigned_by)

```python
class User(BaseModel):
    # R
oreignKey("user_management_user.id"))
    assigned_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user_management_user.id"),
        nullable=True
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_groups",
        foreign_keys=[user_id]
    )
    assigned_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_user_groups",
        foreign_keys=[assigned_by_id]
    )
```

**Utilisation :**
```python
# Deux relations différentes vers le même modèle
user.user_groups           # Groupes auxquels l'user appartient
user.assigned_user_group
s  # Groupes que l'user a assignés à d'autres
user_group.user            # L'user membre
user_group.assigned_by_user # L'user qui a fait l'assignation
```

---

## Exemples Pratiques

### Cas d'Usage 1 : Afficher les Employés avec leurs Postes

**Besoin :** Afficher la liste des employés avec le nom de leur service et groupe.

**Requête :**
```http
GET /api/employees/?expand=poste.service,poste.group
```

**Code Frontend (JavaScript) :**
```javascript
const response = await fetch('/api/employees/?expand=poste.service,poste.group');
const data = await response.json();

data.results.forEach(employee => {
  console.log(`${employee.prenom} ${employee.nom}`);
  console.log(`Service: ${employee.poste.service.titre}`);
  console.log(`Groupe: ${employee.poste.group.name}`);
});
```

### Cas d'Usage 2 : Afficher les Groupes avec leurs Membres

**Besoin :** Afficher un groupe avec tous ses membres (users).

**Requête :**
```http
GET /api/user-groups/?group_id=2&expand=user
```

**Code Front


**Requête :**
```http
GET /api/users/5/?expand=employe,user_groups.group
```

**Réponse :**
```json
{
  "id": 5,
  "email": "john.doe@example.com",
  "nom": "Doe",
  "prenom": "John",
  "employe": {
    "id": 10,
    "matricule": "EMP001",
    "statut_emploi": "ACTIF"
  },
  "user_groups": [
    {
      "id": 1,
      "group_id": 2,
      "group": {
        "id": 2,
        "code": "RRH",
        "name": "Ressources Humaines"
      },
      "is_active": true
    }
  ]
}
```

### Cas d'Usage 4 : Optimiser les Performances

**Problème :** Vous faites N+1 requêtes pour charger les relations.

**❌ Mauvaise Approche (N+1 queries) :**
```javascript
// 1 requête pour les user-groups
const userGroups = await fetch('/api/user-groups/').then(r => r.json());

// N requêtes supplémentaires pour chaque user
for (const ug of userGroups.results) {
  const user = await fetch(`/api/users/${ug.user_id}`).then(r => r.json());
  console.log(user.nom);
}
```

**✅ Bonne Approche (1 seule requête) :**
```javascript
// 1 seule requête avec expand
const userGroups = await fetch('/api/user-groups/?expand=user').then(r => r.json());

for (const ug of userGroups.results) {
  console.log(ug.user.nom);  // Déjà chargé !
}
```

---

## Bonnes Pratiques

### 1. N'Expandez que ce dont

```
→ Maximum 2-3 niveaux

### 3. Utilisez la Pagination avec Expand

✅ **Bon :**
```http
GET /api/e
n fetchWithExpand(endpoint, expand) {
  try {
    const url = expand ? `${endpoint}?expand=${expand}`
Permet: user.employe
    # Expand: ?expand=employe
    employe: Mapped[Optional["Employe"]] = relationship(
        "Employe",
        back_populates="user_account"
    )
```

---

## Résumé

| Concept | Syntaxe | Exemple |
|---------|---------|---------|
| **Expand Simple** | `?expand=relation` | `?expand=user` |
| **Expand Multiple** | `?expand=rel1,rel2` | `?expand=user,group` |
| **Expand Imbriqué** | `?expand=parent.child` | `?expand=user.employe` |
| **Back_Populates** | `back_populates="relation_name"` | `back_populates="user_account"` |

### Points Clés à Retenir

1. **Expand** = Charger les relations automatiquement
2. **Back_Populates** = Navigation bidirectionnelle entre modèles
3. **Performance** = Utilisez expand pour éviter N+1 queries
4. **Modération** = N'expandez que ce dont vous avez besoin

---

## Ressources Supplémentaires

- [Documentation SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/relationships.html)
- [Guide de Dépannage des Erreurs d'Expand](./TROUBLESHOOTING_EXPAND.md) ⚠️
- [Guide des Tests d'Intégration](./TEST_EXPAND_INTEGRATION_README.md)
- [Code Source query_utils.py](./app/core/query_utils.py)

---

## Note sur l'Erreur Corrigée

Si vous rencontrez l'erreur `"does not link from relationship"` lors de l'utilisation d'expand multiples imbriqués (ex: `poste.service,poste.group`), consultez le [guide de dépannage](./TROUBLESHOOTING_EXPAND.md) pour plus de détails sur la correction appliquée.
