# Dépannage des Erreurs d'Expand

## Erreur : "does not link from relationship"

### Symptôme

```
500 Server Error
ArgumentError: ORM mapped entity or attribute "ServiceGroup.group" does not link from relationship "ServiceGroup.service"
```

### Cause

Cette erreur se produit quand vous essayez d'expander plusieurs relations enfants d'un même parent, par exemple :

```http
GET /api/employees/?expand=poste.service,poste.group
```

Le problème vient de la façon dont SQLAlchemy construit les loaders imbriqués. Quand vous avez :
- `poste.service` → Charge `poste` puis `service`
- `poste.group` → Charge `poste` puis `group`

L'ancienne implémentation essayait de chaîner les loaders comme ceci :
```python
loader = selectinload(poste)
loader = loader.selectinload(service)  # OK
loader = loader.selectinload(group)    # ❌ ERREUR !
```

Le deuxième `.selectinload(group)` essaie de charger `group` depuis `service`, pas depuis `poste` !

### Solution

La correction consiste à créer des chaînes de loaders **séparées** pour chaque enfant :

```python
# Pour poste.service
loader1 = selectinload(poste).selectinload(service)
query = query.options(loader1)

# Pour poste.group
loader2 = selectinload(poste).selectinload(group)
query = query.options(loader2)
```

### Code Corrigé

Le fichier `app/core/query_utils.py` a été corrigé :

```python
# Apply nested expansions
for parent, children in nested_expansions.items():
    if hasattr(model, parent):
        parent_attr = getattr(model, parent)

        # Get the related model
        if hasattr(parent_attr.property, 'mapper'):
            related_model = parent_attr.property.mapper.class_

            # For each child, create a separate loader chain
            for child in children:
                if hasattr(related_model, child):
                    # Create a fresh loader chain for each child
                    loader = selectinload(parent_attr).selectinload(
                        getattr(related_model, child)
                    )
                    query = query.options(loader)
```

### Vérification

Après la correction, ces requêtes devraient fonctionner :

```http
# Expand multiple enfants du même parent
GET /api/employees/?expand=poste.service,poste.group

# Expand imbriqué simple
GET /api/user-groups/?expand=user.employe

# Expand multiple parents
GET /api/employees/?expand=poste,user_account
```

---

## Autres Erreurs Courantes

### 1. Relation Inexistante

**Erreur :**
```
AttributeError: type object 'User' has no attribute 'invalid_field'
```

**Cause :** Vous essayez d'expander une relation qui n'existe pas dans le modèle.

**Solution :** Vérifiez les noms des relations dans le modèle :

```python
# Dans models.py
class User(BaseModel):
    employe: Mapped[Optional["Employe"]] = relationship(...)  # ✅ Correct

# Requête
GET /api/users/?expand=employe  # ✅ Correct
GET /api/users/?expand=employee # ❌ Erreur (mauvais nom)
```

### 2. Back_Populates Manquant

**Erreur :**
```
sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize
```

**Cause :** La relation n'a pas de `back_populates` ou il est mal configuré.

**Solution :** Assurez-vous que les deux côtés de la relation ont `back_populates` :

```python
# ❌ Mauvais
class User(BaseModel):
    employe: Mapped[Optional["Employe"]] = relationship("Employe")

class Employe(BaseModel):
    user_account: Mapped[Optional["User"]] = relationship("User")

# ✅ Correct
class User(BaseModel):
    employe: Mapped[Optional["Employe"]] = relationship(
        "Employe",
        back_populates="user_account"  # ← Pointe vers la relation inverse
    )

class Employe(BaseModel):
    user_account: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="employe"  # ← Pointe vers la relation directe
    )
```

### 3. Foreign Key Manquante

**Erreur :**
```
sqlalchemy.exc.NoForeignKeysError: Could not determine join condition
```

**Cause :** La colonne `ForeignKey` n'est pas définie.

**Solution :** Ajoutez la foreign key :

```python
# ❌ Mauvais
class Employe(BaseModel):
    poste_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    poste: Mapped[Optional["ServiceGroup"]] = relationship("ServiceGroup")

# ✅ Correct
class Employe(BaseModel):
    poste_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rh_service_group.id", ondelete="SET NULL"),
        nullable=True
    )
    poste: Mapped[Op
sers/?expand=employe.poste.service
```

### 5. Nom de Champ vs Nom de Relation

**Erreur :** La requête ne retourne pas d'erreur mais l'expand ne fonctionne pas.

**Cause :** Vous utilisez le nom du champ au lieu du nom de la relation.

**Solution :** Utilisez le nom de la **relation**, pas le nom de la **colonne** :

```python
class Employe(BaseModel):
    poste_id: Mapped[int] = mapped_column(ForeignKey(...))  # ← Colonne
    poste: Mapped["ServiceGroup"] = relationship(...)        # ← Relation

# ❌ Mauvais (nom de colonne)
GET /api/employees/?expand=poste_id

# ✅ Correct (nom de relation)
GET /api/employees/?expand=poste
```

---

## Débogage

### 1. Vérifier les Relations Disponibles

Pour voir quelles relations sont disponibles sur un modèle :

```python
from app.user_app.models import Employe
from sqlalchemy.inspection import inspect

# Lister toutes les relations
mapper = inspect(Employe)
for rel in mapper.relationships:
    print(f"Relation: {rel.key}")
    print(f"  → Vers: {rel.mapper.class_.__name__}")
    print(f"  → Back_populates: {rel.back_populates}")
```

### 2. Tester l'Expand Progressivement

Testez d'abord les expansions simples, puis ajoutez les imbriquées :

```http
# Étape 1 : Sans expand
GET /api/employees/

# Étape 2 : Expand simple
GET /api/employees/?expand=poste

# Étape 3 : Expand imbriqué simple
GET /api/employees/?expand=poste.service

# Étape 4 : Expand imbriqué multiple
GET /api/employees/?expand=poste.service,poste.group
```

### 3. Vérifier les Logs SQLAlchemy

Activez les logs SQL pour voir les requêtes générées :

```python
# Dans settings.py ou main.py
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

Vous verrez les requêtes SQL avec les JOINs générés par les expansions.

---

## Checklist de Vérification

Avant d'utiliser un expand, vérifiez :

- [ ] La relation existe dans le modèle
-
[ ] Le nom de la relation est correct (pas le nom de la colonne)
- [ ] `back_populates` est configuré des deux côtés
- [ ] La foreign key est définie
- [ ] La profondeur d'imbrication est raisonnable (≤ 3 niveaux)
- [ ] Les noms correspondent exactement (sensible à la casse)

---

## Ressources

- [Guide d'Utilisation des Expand](./GUIDE_EXPAND_RELATIONS.md)
- [Documentation SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/relationships.html)
- [Code Source query_utils.py](./app/core/query_utils.py)
