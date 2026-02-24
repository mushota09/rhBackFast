# Mise à jour des permissions dans startup.py

## ✅ Modifications effectuées

Le fichier `rhBackFast/app/core/startup.py` a été mis à jour pour inclure TOUTES les permissions spécifiques des apps.

### 1. Dictionnaires de permissions ajoutés

#### AUDIT_PERMISSIONS (1 permission)
```python
AUDIT_PERMISSIONS = {
    "audit.view": "Consulter les logs d'audit",
}
```

#### PAIE_PERMISSIONS (11 permissions)
```python
PAIE_PERMISSIONS = {
    "alert.view": "Consulter les alertes",
    "alert.create": "Créer des alertes",
    "alert.update": "Modifier des alertes",
    "retenue.view": "Consulter les retenues",
    "retenue.create": "Créer des retenues",
    "periode.view": "Consulter les périodes de paie",
    "periode.create": "Créer des périodes de paie",
    "periode.update": "Modifier des périodes de paie",
    "entree.view": "Consulter les entrées de paie",
    "entree.update": "Modifier les entrées de paie",
    "payroll.view": "Consulter et exporter la paie",
}
```

### 2. Fonction create_default_permissions() mise à jour

La fonction a été modifiée pour créer les permissions des trois apps:

- **CONGE_APP**: 8 permissions (déjà existantes)
- **AUDIT_APP**: 1 permission (nouvellement ajoutée)
- **PAIE_APP**: 11 permissions (nouvellement ajoutées)

### 3. Messages de log améliorés

Les messages de log affichent maintenant le nombre de permissions créées par app:

```
✅ Created X new permissions
   - Conge app: X permissions
   - Audit app: X permissions
   - Paie app: X permissions
```

## 📊 Récapitulatif des permissions

| App | Nombre de permissions | Permissions |
|-----|----------------------|-------------|
| **CONGE_APP** | 8 | view, create, update, delete, approve, manage_types, manage_soldes, export |
| **AUDIT_APP** | 1 | view |
| **PAIE_APP** | 11 | alert (view, create, update), retenue (view, create), periode (view, create, update), entree (view, update), payroll (view) |
| **TOTAL** | **20** | |

## 🔧 Fonctionnement

Au démarrage de l'application:

1. La fonction `create_default_permissions()` est appelée
2. Elle crée les permissions CRUD pour tous les modèles
3. Elle crée ensuite les permissions spécifiques pour:
   - conge_app
   - audit_app
   - paie_app
4. Les permissions existantes sont ignorées (pas de doublons)
5. Un rapport détaillé est affiché dans les logs

## ✅ Tests effectués

- ✅ Syntaxe Python validée (aucune erreur)
- ✅ Script de test créé et exécuté avec succès
- ✅ 20 permissions spécifiques aux apps correctement définies
- ✅ Messages de log améliorés pour un meilleur suiv
mer la création

## 🔍 Vérification

Pour vérifier que les permissions sont bien définies, exécutez:

```bash
cd rhBackFast
python test_permissions_startup.py
```

Cela affichera toutes les permissions définies pour chaque app.
