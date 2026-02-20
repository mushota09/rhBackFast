# Documentation du Système d'Expansion - Index

## 📚 Documentation Complète

Bienvenue dans la documentation du système d'expansion de l'API rhBackFast. Cette page vous guide vers les ressources appropriées selon vos besoins.

---

## 🎯 Par Objectif

### Je veux apprendre à utiliser les expansions
👉 **[Guide d'Utilisation des Expand](./GUIDE_EXPAND_RELATIONS.md)**
- Syntaxe complète (simple, multiple, imbriquée)
- Exemples concrets avec requêtes et réponses
- Explication de `back_populates`
- Cas d'usage pratiques
- Bonnes pratiques

### J'ai une erreur avec les expansions
👉 **[Guide de Dépannage](./TROUBLESHOOTING_EXPAND.md)**
- Erreurs courantes et solutions
- Checklist de vérification
- Conseils de débogage
- Exemples de corrections

### Je veux voir tous les cas supportés
👉 **[Cas de Test Complets](./EXPAND_TEST_CASES.md)**
- 12 catégories de tests
- Exemples de requêtes
- Résultats attendus
- Cas limites
- Recommandations de performance

### Je veux tester rapidement
👉 **[Script de Test Manuel](./test_expand_manual.py)**
- Tests automatisés
- Validation rapide
- Exemples d'utilisation

### Je veux un résumé rapide
👉 **[Résumé du Système](./EXPAND_SYSTEM_SUMMARY.md)**
- Vue d'ensemble
- Correction appliquée
- Exemples concrets
- Performance

---

## 📖 Par Type de Document

### Guides Pratiques

| Document | Description | Niveau |
|----------|-------------|--------|
| [GUIDE_EXPAND_RELATIONS.md](./GUIDE_EXPAND_RELATIONS.md) | Guide complet d'utilisation | Débutant → Avancé |
| [TROUBLESHOOTING_EXPAND.md](./TROUBLESHOOTING_EXPAND.md) | Résolution de problèmes | Intermédiaire |
| [EXPAND_SYSTEM_SUMMARY.md](./EXPAND_SYSTEM_SUMMARY.md) | Résumé et vue d'ensemble | Tous niveaux |

### Références Techniques

| Document | Description | Niveau |
|----------|-------------|--------|
| [EXPAND_TEST_CASES.md](./EXPAND_TEST_CASES.md) | Tous les cas testés | Avancé |
| [app/core/query_utils.py](./app/core/query_utils.py) | Code source | Développeur |
| [test_expand_manual.py](./test_expand_manual.py) | Script de test | Développeur |

### Tests

| Document | Description | Type |
|----------|-------------|------|
| [test_expand_integration.py](./test_expand_integration.py) | Tests d'intégration automatisés | Pytest |
| [test_expand_manual.py](./test_expand_manual.py) | Tests manuels avec requests | Python |
| [TEST_EXPAND_INTEGRATION_README.md](./TEST_EXPAND_INTEGRATION_README.md) | Guide des tests d'intégration | Documentation |

---

## 🚀 Démarrage Rapide

### 1. Première Utilisation (5 minutes)

```http
# Test simple
GET /api/employees/?expand=poste

# Test multiple
GET /api/employees/?expand=poste,user_account

# Test imbriqué
GET /api/employees/?expand=poste.service
```

📖 **Lire :** [Guide d'Utilisation - Section Expand Simple](./GUIDE_EXPAND_RELATIONS.md#expand-simple)

### 2. Cas Avancés (10 minutes)

```http
# Expansion imbriquée multiple
GET /api/employees/?expand=poste.service,poste.group

# Expansion profonde
GET /api/user-groups/?expand=user.employe.poste

# Expansion mixte
GET /api/employees/?expand=responsable,poste.service
```

📖 **Lire :** [Guide d'Utilisation - Section Expand Imbriqué](./GUIDE_EXPAND_RELATIONS.md#expand-imbriqué-nested)

### 3. Comprendre Back_Populates (15 minutes)

```python
# Configuration des relations bidirectionnelles
class User(BaseModel):
    employe: Mapped[Optional["Employe"]] = relationship(
        "Employe",
        back_populates="user_account"
    )
```

📖 **Lire :** [Guide d'Utilisation - Section Back_Populates](./GUIDE_EXPAND_RELATIONS.md#back_populates)

---

## 🔍 Par Problème Spécifique

### Erreur : "does not link from relationship"
👉 [TROUBLESHOOTING_EXPAND.md - Section Erreur Principale](./TROUBLESHOOTING_EXPAND.md#erreur--does-not-link-from-relationship)

### Expansion ne fonctionne pas
👉 [TROUBLESHOOTING_EXPAND.md - Section Relation Inexistante](./TROUBLESHOOTING_EXPAND.md#1-relation-inexistante)

### Performance lente
👉 [EXPAND_TEST_CASES.md - Section Performance](./EXPAND_TEST_CASES.md#-performance)

### Relation NULL
👉 [EXPAND_TEST_CASES.md - Section Cas Limites](./EXPAND_TEST_CASES.md#3-expansion-de-relations-optionnelles-null)

---

## 💡 Exemples par Endpoint

### Employees
```http
# Simple
GET /api/employees/?expand=poste
GET /api/employees/?expand=user_account
GET /api/employees/?expand=responsable

# Multiple
GET /api/employees/?expand=poste,user_account
GET /api/employees/?expand=poste,user_account,responsable

# Imbriqué
GET /api/employees/?expand=poste.service
GET /api/employees/?expand=poste.group
GET /api/employees/?expand=poste.service,poste.group
GET /api/employees/?expand=user_account.user_groups
```

### User-Groups
```http
# Simple
GET /api/user-groups/?expand=user
GET /api/user-groups/?expand=group

# Multiple
GET /api/user-groups/?expand=user,group
GET /api/user-groups/?expand=user,group,assigned_by_user

# Imbriqué
GET /api/user-groups/?expand=user.employe
GET /api/user-groups/?expand=group.service_groups
GET /api/user-groups/?expand=user.employe.poste
```

### Service-Groups
```http
# Simple
GET /api/service-groups/?expand=service
GET /api/service-groups/?expand=group

# Multiple
GET /api/service-groups/?expand=service,group
```

---

## 🎓 Parcours d'Apprentissage

### Niveau Débutant (30 minutes)
1. Lire [EXPAND_SYSTEM_SUMMARY.md](./EXPAND_SYSTEM_SUMMARY.md)
2.Tester les exemples simples du [Guide d'Utilisation](./GUIDE_EXPAND_RELATIONS.md)
3. Exécuter [test_expand_manual.py](./test_expand_manual.py)

### Niveau Intermédiaire (1 heure)
1. Lire le [Guide Complet](./GUIDE_EXPAND_RELATIONS.md)
2. Comprendre [Back_Populates](./GUIDE_EXPAND_RELATIONS.md#back_populates)
3. Tester les cas avancés
4. Lire le [Guide de Dépannage](./TROUBLESHOOTING_EXPAND.md)

### Niveau Avancé (2 heures)
1. Étudier [tous les cas de test](./EXPAND_TEST_CASES.md)
2. Analyser le [code source](./app/core/query_utils.py)
3. Créer des tests personnalisés
4. Optimiser les performances

---

## 🛠️ Outils et Scripts

### Scripts Python
- **[test_expand_manual.py](./test_expand_manual.py)** - Tests manuels rapides
- **[test_expand_integration.py](./test_expand_integration.py)** - Tests d'intégration pytest

### Commandes Utiles

```bash
# Lancer les tests d'intégration
pytest test_expand_integration.py -v

# Lancer les tests manuels
python test_expand_manual.py

# Tester une expansion spécifique
curl "http://localhost:8000/api/employees/?expand=poste.service"
```

---

## 📊 Statistiques

### Documentation
- **5 documents** de référence
- **2 scripts** de test
- **50+ exemples** concrets
- **12 catégories** de cas testés

### Couverture
- ✅ Expansions simples
- ✅ Expansions multiples
- ✅ Expansions imbriquées (jusqu'à 4 niveaux)
- ✅ Combinaisons avec filtres, pagination, ordering
- ✅ Gestion des erreurs
- ✅ Optimisation des performances

---

## 🔗 Liens Externes

- [Documentation SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/relationships.html)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Pydantic](https://docs.pydantic.dev/)

---

## 📞 Support

### En cas de problème
1. Consultez le [Guide de Dépannage](./TROUBLESHOOTING_EXPAND.md)
2. Vérifiez les [Cas de Test](./EXPAND_TEST_CASES.md)
3. Examinez le [Code Source](./app/core/query_utils.py)

### Pour contribuer
- Ajoutez des exemples dans les guides
- Créez des tests supplémentaires
- Documentez les cas d'usage spécifiques

---

## 📝 Changelog

### Version 2.0 (Actuelle)
- ✅ Correction de l'erreur "does not link from relationship"
- ✅ Support des expansions imbriquées multiples
- ✅ Amélioration de la robustesse
- ✅ Documentation complète

### Version 1.0
- ✅ Implémentation initiale
- ✅ Support des expansions simples et imbriquées

---

**Dernière mise à jour :** Février 2026
**Statut :** ✅ Stable et Production-Ready

