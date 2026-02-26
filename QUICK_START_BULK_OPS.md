# Guide de Démarrage Rapide - Opérations Bulk

## 🚀 Démarrage en 5 Minutes

### Étape 1: Vérifier l'Installation

Les endpoints bulk sont déjà implémentés dans votre backend. Vérifiez que vous avez:

```bash
# Vérifier que les fichiers ont été modifiés
ls -la app/user_app/routes.py
ls -la app/user_app/schemas.py
```

### Étape 2: Démarrer le Serveur

```bash
# Depuis le dossier rhBackFast
uvicorn main:app --reload
```

Le serveur démarre sur `http://localhost:8000`

### Étape 3: Tester les Endpoints

#### Option A: Utiliser le Script de Test (Recommandé)

```bash
# Dans un nouveau terminal
python test_bulk_operations.py
```

#### Option B: Tester Manuellement avec curl

```bash
# 1. S'authentifier
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.access')

# 2. Tester bulk assign
curl -X POST "http://localhost:8000/api/user-groups/bulk-assign/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [1, 2],
    "group_ids": [1],
    "is_active": true,
    "replace_existing": false
  }' | jq

# 3. Tester bulk update permissions
curl -X POST "http://localhost:8000/api/group-permissions/bulk-update/1/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "permissions": [
      {"permission_id": 1, "granted": true},
      {"permission_id": 2, "granted": false}
    ]
  }' | jq

# 4. Tester bulk remove
curl -X POST "http://localhost:8000/api/user-groups/bulk-remove/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [1, 2],
    "group_ids": [1]
  }' | jq
```

#### Option C: Utiliser Swagger UI

1. Ouvrir `http://localhost:8000/docs`
2. Cliquer sur "Authorize" et entrer votre token
3. Tester les endpoints:
   - `POST /api/user-groups/bulk-assign/`
   - `POST /api/user-groups/bulk-remove/`
   - `POST /api/group-permissions/bulk-update/{group_id}/`

---

## 📋 Checklist de Vérification

- [ ] Le serveur démarre sans erreur
- [ ] Les endpoints apparaissent dans Swagger UI
- [ ] L'authentification fonctionne
- [ ] Bulk assign retourne un succès
- [ ] Bulk update permissions retourne un succès
- [ ] Bulk remove retourne un succès
- [ ] Les erreurs de validation sont gérées correctement

---

## 🎯 Cas d'Usage Rapides

### Cas 1: Assigner Tous les Nouveaux Employés à un Groupe

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "your_access_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Assigner les utilisateurs 1, 2, 3 au groupe 1
response = requests.post(
    f"{BASE_URL}/api/user-groups/bulk-assign/",
    headers=headers,
    json={
        "user_ids": [1, 2, 3],
        "group_ids": [1],
        "is_active": True,
        "replace_existing": False
    }
)

print(response.json())
# Output: {"success": true, "created_count": 3, ...}
```

### Cas 2: Configurer les Permissions d'un Nouveau Groupe

```python
# Définir toutes les permissions pour le groupe 2
response = requests.post(
    f"{BASE_URL}/api/group-permissions/bulk-update/2/",
    headers=headers,
    json={
        "permissions": [
            {"permission_id": 1, "granted": True},   # READ
            {"permission_id": 2, "granted": True},   # CREATE
            {"permission_id": 3, "granted": True},   # UPDATE
            {"permission_id": 4, "granted": False},  # DELETE
        ]
    }
)

print(response.json())
# Output: {"success": true, "created_count": 4, ...}
```

### Cas 3: Retirer des Utilisateurs d'un Groupe Temporaire

```python
# Retirer les utilisateurs 1, 2, 3 du groupe 5
response = requests.post(
    f"{BASE_URL}/api/user-groups/bulk-remove/",
    headers=headers,
    json={
        "user_ids": [1, 2, 3],
        "group_ids": [5]
    }
)

print(response.json())
# Output: {"success": true, "deleted_count": 3, ...}
```

---

## 🔍 Vérification des Résultats

### Vérifier les Assignations

```bash
# Lister toutes les assignations d'un utilisateur
curl "http://localhost:8000/api/user-groups/?user_id=1" \
  -H "Authorization: Bearer $TOKEN" | jq

# Lister toutes les assignations d'un groupe
curl "http://localhost:8000/api/user-groups/?group_id=1" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Vérifier les Permissions

```bash
# Lister toutes les permissions d'un groupe
curl "http://localhost:8000/api/group-permissions/?group_id=1" \
  -H "Authorization: Bearer $TOKEN" | jq

# Obtenir les permissions effectives d'un utilisateur
curl "http://localhost:8000/api/group-permissions/users/1/permissions" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## ⚠️ Problèmes Courants

### Problème 1: "401 Unauthorized"

**Cause**: Token invalide ou expiré

**Solution**:
```bash
# Obtenir un nouveau token
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.access')
```

### Problème 2: "User with ID X not found"

**Cause**: L'utilisateur n'existe pas

**Solution**:
```bash
# Vérifier les utilisateurs existants
curl "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer $TOKEN" | jq '.results[].id'
```

### Problème 3: "Group with ID X not found"

**Cause**: Le groupe n'existe pas

**Solution**:
```bash
# Vérifier les groupes existants
curl "http://localhost:8000/api/groups/" \
  -H "Authorization: Bearer $TOKEN" | jq '.results[].id'
```

### Problème 4: "Permission with ID X not found"

**Cause**: La permission n'existe pas

**Solution**:
```bash
# Vérifier les permissions existantes
curl "http://localhost:8000/api/permissions/" \
  -H "Authorization: Bearer $TOKEN" | jq '.results[].id'
```

---

## 📚 Documentation Complète

Pour plus de détails, consultez:

1. **Documentation technique**: `documentation_fonctionnalite/BULK_OPERATIONS_IMPLEMENTATION.md`
2. **Résumé**: `BULK_OPERATIONS_SUMMARY.md`
3. **Code source**: `app/user_app/routes.py` (lignes 1945-2250)

---

## 🎉 Prochaines Étapes

Une fois les tests réussis:

1. ✅ Intégrer avec le frontend hr_management
2. ✅ Tester les composants BulkUserAssignment et GroupPermissionMatrix
3. ✅ Déployer en environnement de staging
4. ✅ Former l'équipe sur les nouvelles fonctionnalités

---

## 💡 Conseils

- **Performance**: Limitez à 100 utilisateurs et 50 groupes par requête
- **Erreurs**: Les opérations continuent même si certaines échouent
- **Transactions**: Toutes les opérations sont dans une transaction unique
- **Validation**: Tous les IDs sont validés avant le traitement

---

## 🆘 Besoin d'Aide?

1. Vérifier les logs du serveur
2. Consulter la documentation complète
3. Exécuter le script de test avec mode verbose
4. Vérifier la base de données directement

---

**Bon développement! 🚀**
