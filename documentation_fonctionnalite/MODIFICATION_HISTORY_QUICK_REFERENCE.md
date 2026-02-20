# Référence Rapide - Historique des Modifications

## 🚀 Démarrage Rapide

### Consulter l'historique d'une entrée de paie

```bash
GET /api/payroll/history/entrees/{entree_id}
Authorization: Bearer {token}
```

### Consulter l'historique d'une retenue

```bash
GET /api/payroll/history/retenues/{retenue_id}
Authorization: Bearer {token}
```

## 💻 Code Examples

### Suivre une modification

```python
from app.paie_app.services import ModificationHistoryService

# Capturer les anciennes valeurs
old_values = ModificationHistoryService.extract_model_values(entree)

# Effectuer la modification
entree.salaire_base = new_amount

# Capturer les nouvelles valeurs
new_values = ModificationHistoryService.extract_model_values(entree)

# Enregistrer l'historique
await ModificationHistoryService.track_entree_modification(
    db=db,
    entree=entree,
    user=current_user,
    action="UPDATE",
    old_values=old_values,
    new_values=new_values,
    reason="Correction manuelle"
)
```

### Récupérer l'historique

```python
# Pour une entrée de paie
history = await ModificationHistoryService.get_entree_history(db, entree_id)

# Pour une retenue
history = await ModificationHistoryService.get_retenue_history(db, retenue_id)

# Afficher
for record in history:
    print(f"{record['timestamp']}: {record['action']} by {record['user_name']}")
```

## 📋 Types d'Actions

| Action | Description | Utilisation |
|--------|-------------|-------------|
| `CREATE` | Création initiale | Nouvelle entrée/retenue |
| `UPDATE` | Modification manuelle | Correction, ajustement |
| `RECALCULATE` | Recalcul automatique | Traitement de période |
| `APPLY` | Application de retenue | Déduction appliquée |
| `VALIDATE` | Validation | Entrée validée |
| `DEACTIVATE` | Désactivation | Retenue désactivée |

## 🔐 Permissions

| Endpoint | Permission Requise |
|----------|-------------------|
| `GET /history/entrees/{id}` | `entree.view` |
| `GET /history/retenues/{id}` | `retenue.view` |

## 📊 Format de Réponse

```json
{
  "resource_type": "entree_paie",
  "resource_id": 123,
  "total_modifications": 2,
  "history": [
    {
      "timestamp": "2024-02-17T10:30:00",
      "user_id": 5,
      "user_name": "Dupont Jean",
      "user_email": "jean.dupont@example.com",
      "action": "CREATE",
      "reason": "Period processing",
      "changes": {}
    }
  ]
}
```

## ⚡ Intégration Automatique

### Services avec Suivi Automatique

1. **PeriodProcessorService**
   - `process_period()` → Suit CREATE et RECALCULATE

2. **DeductionManagerService**
   - `create_deduction()` → Suit CREATE
   - `update_deduction_balance()` → Suit APPLY

## 🎯 Cas d'Usage Courants

### 1. Vérifier qui a modifié un salaire

```python
history = await ModificationHistoryService.get_entree_history(db, entree_id)
updates = [r for r in history if r['action'] == 'UPDATE']
for update in updates:
    print(f"{update['user_name']} - {update['timestamp']}")
    print(f"Changements: {update['changes']}")
```

### 2. Tracer les applications de retenue

```python
history = await ModificationHistoryService.get_retenue_history(db, retenue_id)
applications = [r for r in history if r['action'] == 'APPLY']
total_applied = sum(
    r['changes']['montant_deja_deduit']['new']
    for r in applications
)
print(f"Total appliqué: {total_applied}")
```

### 3. Compter les modifications d'une entrée

```python
history = await ModificationHistoryService.get_entree_history(db, entree_id)
print(f"Nombre de modifications: {len(history)}")
```

## 🔧 Configuration

Aucune configuration requise - le système est activé par défaut.

## 📝 Notes Importantes

- ✅ L'historique est stocké dans le modèle (JSON)
- ✅ Pas de limite de taille d'historique
- ✅ Les modifications sont tracées automatiquement
- ✅ Aucun impact sur les performances
- ⚠️ Toujours fournir une raison pour les modifications manuelles

## 🐛 Dépannage

### L'historique est vide

```python
# Vérifier que l'entrée existe
entree = await db.get(EntreePaie, entree_id)
if not entree:
    print("Entrée introuvable")

# Vérifier le champ
if not entree.modification_history:
    print("Aucune modification enregistrée")
```

### Les modifications ne sont pas enregistrées

```python
# S'assurer de passer l'utilisateur
await service.create_deduction(data, user=current_user)  # ✅
await service.create_deduction(data)  # ❌ Pas de suivi
```

## 📚 Documentation Complète

Voir `MODIFICATION_HISTORY_GUIDE.md` pour la documentation complète.

---

**Version** : 1.0
**Dernière mise à jour** : 2024-02-17
