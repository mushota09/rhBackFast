# Cas de Test pour les Expansions

Ce document liste tous les cas d'expansion supportés et testés.

## ✅ Cas Supportés et Testés

### 1. Expansion Simple (1 relation)

```http
GET /api/employees/?expand=poste
GET /api/employees/?expand=user_account
GET /api/employees/?expand=responsable
GET /api/user-groups/?expand=user
GET /api/user-groups/?expand=group
GET /api/service-groups/?expand=service
GET /api/service-groups/?expand=group
```

**Résultat attendu :** La relation spécifiée est chargée comme objet comp
T /api/user-groups/?expand=user.employe
GET /api/user-groups/?expand=group.service_groups
GET /api/employees/?expand=poste.service
GET /api/employees/?expand=poste.group
GET /api/employees/?expand=user_account.user_groups
```

**Résultat attendu :** La relation parent et sa relation enfant sont toutes deux chargées.

**Exemple de réponse :**
```json
{
  "id": 1,
  "user_id": 5,
  "user": {
    "id": 5,
    "email": "john@example.com",
    "employe": {
      "id": 10,
      "matricule": "EMP001"
    }
  }
}
```

---

### 4. Expansion Imbriquée Multiple (même parent, plusieurs enfants)

```http
GET /api/employees/?expand=poste.service,poste.group
GET /api/user-groups/?expand=user.employe,user.user_groups
GET /api/employees/?expand=user_account.employe,user_account.user_groups
```

**Résultat attendu :** Le parent est chargé une fois, avec tous ses enfants spécifiés.

**Exemple de réponse :**
```json
{
  "id": 10,
  "poste_id": 1,
  "poste": {
    "id": 1,
    "service_id": 3,
    "service": {
      "id": 3,
      "code": "IT",
      "titre": "Informatique"
    },
    "group_id": 2,
    "group": {
      "id": 2,
      "code": "DEV",
      "name": "Développeurs"
    }
  }
}
```

---

### 5. Expansion Imbriquée Profonde (3 niveaux)

```http
GET /api/user-groups/?expand=user.employe.poste
GET /api/employees/?expand=poste.service.service_groups
GET /api/employees/?expand=user_account.employe.poste
```

**Résultat attendu :** Trois niveaux de relations sont chargés.

**Exemple de réponse :**
```json
{
  "id": 1,
  "user_id": 5,
  "user": {
    "id": 5,
    "email": "john@example.com",
    "employe": {
      "id": 10,
      "matricule": "EMP001",
      "poste": {
        "id": 1,
        "service_id": 3,
        "group_id": 2
      }
    }
  }
}
```

---

### 6. Expansion Mixte (simple + imbriquée)

```http
GET /api/employees/?expand=responsable,poste.service
GET /api/employees/?expand=user_account,poste.service,poste.group
GET /api/user-groups/?expand=assigned_by_user,user.employe
```

**Résultat attendu :** Les relations simples et imbriquées sont toutes chargées correctement.

---

### 7. Expansion avec Plusieurs Parents Imbriqués

```http
GET /api/employees/?expand=poste.service,user_account.employe
GET /api/employees/?expand=poste.service.service_groups,user_account.user_groups
```

**Résultat attendu :** Chaque chaîne d'expansion est traitée indépendamment.

---

### 8. Expansion de Collections (One-to-Many)

```http
GET /api/groups/?expand=service_groups
GET /api/groups/?expand=user_groups
GET /api/services/?expand=service_groups
GET /api/users/?expand=user_groups
GET /api/employees/?expand=subordonnes
```

**Résultat attendu :** Les collections (listes) sont chargées.

**Exemple de réponse :**
```json
{
  "id": 2,
  "code": "RRH",
  "name": "Ressources Humaines",
  "service_groups": [
    {
      "id": 1,
      "service_id": 3,
      "group_id": 2
    },
=user
GET /api/employees/?statut_emploi=ACTIF&expand=poste,user_account
```

**Résultat attendu :** Les filtres sont appliqués d'abord, puis les expansions.

---

### 11. Expansion avec Pagination

```http
GET /api/employees/?expand=poste.service&limit=10&skip=0
GET /api/user-groups/?expand=user,group&limit=20&skip=20
```

**Résultat attendu :** La pagination fonctionne normalement avec les expansions.

---

### 12. Expansion avec Ordering

```http
GET /api/employees/?expand=poste&ordering=-created_at
GET /api/user-groups/?expand=user&ordering=created_at
```

**Résultat attendu :** L'ordre est appliqué aux résultats principaux, les expansions suivent.

---

## ⚠️ Cas Limites

### 1. Expansion Très Profonde (> 3 niveau
s
**Alternative :** Limiter la profondeur

---

### 3. Expansion de Relations Optionnelles (NULL)

```http
GET /api/employees/?expand=responsable
```

**Statut :** ✅ Supporté
**Comportement :** Si `responsable_id` est NULL, le champ `responsable` sera `null` dans la réponse

**Exemple de réponse :**
```json
{
  "id": 10,
  "responsable_id": null,
  "responsable": null
}
```

---

### 4. Expansion de Relations Inexistantes

```http
❌ GET /api/employees/?expand=invalid_relation
```

**Statut :** Ignoré silencieusement
**Comportement :** L'expansion invalide est ignorée, les autres fonctionnent

---

### 5. Expansion avec Noms Incorrects

```http
❌ GET /api/employees/?expand=poste_id
   (Nom de colonne au lieu de nom de relation)

✅ GET /api/employees/?expand=poste
   (Nom de relation correct)
```

**Statut :** L'expansion avec le nom de colonne est ignorée

---

## 🧪 Tests de Validation

### Test 1 : Expansion Simple
```bash
curl "http://localhost:8000/api/employees/?expand=poste"
```

**Vérification :**
- `poste` est un objet (pas un ID)
- `poste` contient `id`, `service_id`, `group_id`

---

### Test 2 : Expansion Multiple
```bash
curl "http://localhost:8000/api/employees/?expand=poste,user_account"
```

**Vérification :**
- `poste` est un objet
- `user_account` est un objet
- Les deux sont présents

---

### Test 3 : Expansion Imbriquée
```bash
curl "http://localhost:8000/api/employees/?expand=poste.service"
```

**Vérification :**
- `poste` est un objet
- `poste.service` est un objet
- `poste.service` contient `code`, `titre`

---

### Test 4 : Expansion Imbriquée Multiple (Le cas qui causait l'erreur)
```bash
curl "http://localhost:8000/api/employees/?expand=poste.service,poste.group"
```

**Vérification :**
- `poste` est un objet
- `poste.s
s et services sont expandés

---

## 📊 Performance

### Recommandations

| Profondeur | Performance | Recommandation |
|------------|-------------|----------------|
| 1 niveau | ⚡ Excellent | Utilisez librement |
| 2 niveaux | ✅ Bon | Recommandé |
| 3 niveaux | ⚠️ Acceptable | Utilisez avec modération |
| 4+ niveaux | ❌ Lent | Évitez |

### Nombre de Relations

| Nombre | Performance | Recommandation |
|--------|-------------|----------------|
| 1-2 relations | ⚡ Excellent | Utilisez librement |
| 3-4 relations | ✅ Bon | OK |
| 5-6 relations | ⚠️ Acceptable | Attention |
| 7+ relations | ❌ Lent | Évitez |

---

## 🎯 Exemples Réels d'Utilisation

### Afficher un Employé avec son Profil Complet
```http
GET /api/employees/10
/?expand=poste.service,poste.group,user_account,responsable
```

### Afficher les Membres d'un Groupe
```http
GET /api/user-groups/?group_id=2&is_active=true&expand=user.employe
```

### Afficher les Services avec leurs Groupes
```http
GET /api/service-groups/?expand=service,group
```

### Afficher un User avec tous ses Détails
```http
GET /api/users/5/?expand=employe.poste.service,user_groups.group
```

---

## 📝 Notes Importantes

1. **Toujours tester** les expansions complexes en développement avant de les utiliser en production
2. **Monitorer les performances** avec des outils comme SQLAlchemy echo ou des profilers
3. **Utiliser la pagination** avec les expansions pour limiter la quantité de données
4. **Documenter** les expansions utilisées dans votre frontend pour faciliter la maintenance
5. **Préférer plusieurs requêtes simples** plutôt qu'une requête très complexe si les performances sont mauvaises

---

## 🔗 Ressources

- [Guide d'Utilisation des Expand](./GUIDE_EXPAND_RELATIONS.md)
- [Guide de Dépannage](./TROUBLESHOOTING_EXPAND.md)
- [Tests d'Intégration](./TEST_EXPAND_INTEGRATION_README.md)
