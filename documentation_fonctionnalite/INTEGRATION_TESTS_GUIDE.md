# Guide des Tests d'Intégration

## 📋 Vue d'ensemble

Ce document décrit les tests d'intégration pour le système RH FastAPI.

## ✅ Tests de Structure (Complétés)

**Fichier**: `tests/test_simple_structure.py`
**Statut**: ✅ 6/6 tests passés (100%)
**Temps d'exécution**: ~3 secondes

Ces tests vérifient que tous les modules peuvent être importés correctement.

## 🔄 Tests d'Intégration avec Base de Données

### Prérequis

1. **Base de données PostgreSQL** configurée et accessible
2. **Variables d'environnement** correctement définies dans `.env`
3. **Migrations** appliquées avec Alembic

### Configuration

Le fichi
r**:
- ✅ Service
- ✅ User
- ✅ Employe
- ✅ Contrat
- ✅ Alert
- ✅ RetenueEmploye
- ✅ PeriodePaie
- ✅ EntreePaie

#### 2. Tests de Relations

**Objectif**: Vérifier les relations entre entités

```python
async def test_employee_service_relationship():
    # Créer service
    # Créer employé avec service_id
    # Vérifier la relation
```

**Relations à tester**:
- Service ↔ Employe
- Employe ↔ Contrat
- Employe ↔ User
- PeriodePaie ↔ EntreePaie
- Employe ↔ RetenueEmploye

#### 3. Tests de Workflow Paie

**Objectif**: Tester le workflow complet de paie

```python
async def test_complete_payroll_workflow():
    # 1. Créer employé avec contrat
    # 2. Créer période de paie
    # 3. Traiter la période (calcul)
    # 4. Vérifier les entrées de paie
    # 5. Finaliser la période
    # 6. Approuver la période
```

**Étapes du workflow**:
1. DRAFT → Création de période
2. PROCESSING → Calcul en cours
3. COMPLETED → Calcul terminé
4. FINALIZED → Période verrouillée
5. APPROVED → Période approuvée

#### 4. Tests de Calcul de Salaire

**Objectif**: Vérifier les calculs de paie

```python
async def test_salary_calculation():
    # Salaire de base: 500,000 FC
    # Indemnité logement: 100,000 FC
    # Vérifier: salaire_brut, cotisations, IRE, net
```

**Calculs à vérifier**:
- Salaire brut = base + indemnités
- Cotisations INSS (6% patronal, 4% employé)
- IRE (impôt progressif)
- Salaire net = brut - cotisations - IRE - retenues

#### 5. Tests de Retenues

**Objectif**: Vérifier la gestion des retenues

```python
async def test_deduction_application():
    # Créer retenue de 50,000 FC/mois
    # Traiter période
    # Vérifier que retenue est appliquée
    # Vérifier mise à jour du solde
```

**Scénarios**:
- Retenue unique
- Retenues multiples
- Retenue récurrente
- Retenue terminée (solde = 0)

#### 6. Tests d'Audit

**Objectif**: Vérifier la journalisation

```python
async def test_audit_logging():
    # Créer une entité
    # Vérifier qu'un log d'audit est créé
    # Vérifier les détails du log
```

**Actions à auditer**:
- CREATE
- UPDATE
- DELETE
- EXPORT
- APPROVE

#### 7. Tests d'Alertes

**Objectif**: Vérifier le système d'alertes

```python
async def test_alert_creation():
    # Créer alerte
    # Vérifier sévérité
    # Vérifier statut
```

**Types d'alertes**:
- MISSING_DATA
- CALCULATION_ERROR
- VALIDATION_ERROR

### Commandes de Test

#### Exécuter tous les tests
```bash
python -m pytest tests/ -v
```

#### Exécuter tests d'intégration uniquement
```bash
python -m pytest tests/test_integration_*.py -v
```

#### Exécuter un test spécifique
```bash
python -m pytest tests/test_integration_db.py::test_create_service -v
```

#### Avec sortie détaillée
```bash
python -m pytest tests/ -v -s
```

#### Avec couverture de code
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

### Problèmes Connus

#### 1. Noms de Colonnes

Les modèles utilisent des noms spécifiques:
- Service: `titre` (pas `nom`)
- User: `password` (pas `hashed_password`)
- User: `nom` et `prenom` (pas `username`)

#### 2. Temps d'Exécution

Les tests d'intégration avec base de données sont lents:
- Création/suppression de tables: ~30s
- Tests complets: 5-10 minutes

**Solution**: Utiliser des tests de structure pour validation rapide

#### 3. Connexion Base de Données

Les tests nécessitent une connexion active à PostgreSQL.

**Solution**: Vérifier la configuration dans `conftest.py`

### Bonnes Pratiques

1. **Isolation des Tests**
   - Chaque test doit être indépendant
   - Utiliser des transactions avec rollback
   - Ne pas dépendre de l'ordre d'exécution

2. **Données de Test**
   - Utiliser des données réalistes
   - Nettoyer après chaque test
   - Utiliser des fixtures pour données communes

3. **Assertions**
   - Vérifier les valeurs importantes
   - Tester les cas limites
   - Vérifier les erreurs attendues

4. **Performance**
   - Minimiser les opérations de base de données
   - Utiliser des transactions
   - Grouper les tests similaires

### Structure Recommandée

```
tests/
├── conftest.py                 # Configuration pytest
├── test_simple_structure.py    # Tests rapides (✅ Complété)
├── test_integration_user.py    # Tests user_app
├── test_integration_audit.py   # Tests audit_app
├── test_integration_paie.py    # Tests paie_app
└── test_integration_workflow.py # Tests workflow complet
```

### Métriques Cibles

| Métrique | Cible |
|----------|-------|
| Couverture de code | > 80% |
| Tests passés | 100% |
| Temps d'exécution | < 10 min |
| Tests par module | > 10 |

### Prochaines Étapes

1. ✅ Tests de structure - COMPLÉTÉ
2. ⏳ Tests CRUD de base
3. ⏳ Tests de relations
4. ⏳ Tests de workflow paie
5. ⏳ Tests de calcul
6. ⏳ Tests de retenues
7. ⏳ Tests d'audit
8. ⏳ Tests d'alertes

---

**Dernière mise à jour**: 2024-02-17
**Statut**: Tests de structure validés, tests d'intégration en attente

