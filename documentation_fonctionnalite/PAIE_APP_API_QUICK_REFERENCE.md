# API Paie - Référence Rapide

## Base URL
```
/api/paie
```

## Alertes

| Méthode | Endpoint | Permission | Description |
|---------|----------|------------|-------------|
| GET | `/alerts` | alert.view | Liste des alertes |
| POST | `/alerts` | alert.create | Créer une alerte |
| GET | `/alerts/{id}` | alert.view | Détails d'une alerte |
| POST | `/alerts/{id}/send-notification` | alert.update | Envoyer notification |

## Retenues

| Méthode | Endpoint | Permission | Description |
|---------|----------|------------|-------------|
| GET | `/retenues` | retenue.view | Liste des retenues |
| POST | `/retenues` | retenue.create | Créer une retenue |

**Paramètres de requête**:
- `employe_id`: Filtrer par employé

## Périodes de Paie

| Méthode | Endpoint | Permission | Description |
|---------|----------|------------|-------------|
| GET | `/periodes` | periode.view | Liste des périodes |
| POST | `/periodes` | periode.create | Créer une période |
| POST | `/periodes/{id}/process` | periode.update | Traiter (calculer) |
| POST | `/periodes/{id}/finalize` | periode.update | Finaliser |
| POST | `/periodes/{id}/approve` | periode.update | Approuver |

**Paramètres de requête**:
- `annee`: Filtrer par année
- `mois`: Filtrer par mois (1-12)

## Entrées de Paie

| Méthode | Endpoint | Permission | Description |
|---------|----------|------------|-------------|
| GET | `/entrees` | entree.view | Liste des entrées |
| POST | `/entrees/{id}/calculate` | entree.update | Recalculer |

**Paramètres de requête**:
- `periode_id`: Filtrer par période

## Export

| Méthode | Endpoint | Permission | Description |
|---------|----------|------------|-------------|
| GET | `/payroll/export/periode/{id}` | payroll.view | Exporter une période |
| GET | `/payroll/export/all-periodes` | payroll.view | Exporter toutes périodes |
| GET | `/payroll/export/retenues` | payroll.view | Exporter retenues |

**Paramètres de requête**:
- `export_format`: `excel` ou `csv` (défaut: excel)
- `annee`: Filtrer par année (all-periodes)
- `employe_id`: Filtrer par employé (retenues)


## Bulletins de Paie (PDF)

| Méthode | Endpoint | Permission | Description |
|---------|----------|------------|-------------|
| POST | `/payroll/entrees/{id}/generate-payslip` | entree.view | Générer un bulletin |
| GET | `/payroll/entrees/{id}/download-payslip` | entree.view | Télécharger bulletin |
| POST | `/payroll/periodes/{id}/generate-all-payslips` | periode.view | Générer tous bulletins |

## Statistiques

| Méthode | Endpoint | Permission | Description |
|---------|----------|------------|-------------|
| GET | `/statistics/periode/{id}/summary` | payroll.view | Résumé période |
| GET | `/statistics/annual/{annee}/summary` | payroll.view | Résumé annuel |
| GET | `/statistics/employee/{id}/history` | payroll.view | Historique employé |
| GET | `/statistics/deductions/summary` | retenue.view | Résumé retenues |
| GET | `/statistics/alerts/summary` | alert.view | Résumé alertes |
| GET | `/statistics/comparative/{annee}/{mois}` | payroll.view | Analyse comparative |
| GET | `/statistics/top-earners` | payroll.view | Top salaires |
| GET | `/statistics/dashboard` | payroll.view | Tableau de bord |

**Paramètres de requête courants**:
- `annee`: Année
- `mois`: Mois (1-12)
- `limit`: Nombre de résultats
- `employe_id`: Filtrer par employé
- `periode_id`: Filtrer par période
- `compare_to_previous`: true/false (comparative)

## Historique des Modifications

| Méthode | Endpoint | Permission | Description |
|---------|----------|------------|-------------|
| GET | `/history/entrees/{id}` | entree.view | Historique entrée |
| GET | `/history/retenues/{id}` | retenue.view | Historique retenue |

## Workflow Rapide

### Traitement Mensuel
```bash
# 1. Créer période
POST /periodes {"annee": 2024, "mois": 3, ...}

# 2. Traiter
POST /periodes/1/process

# 3. Vérifier alertes
GET /alerts?periode_id=1

# 4. Finaliser
POST /periodes/1/finalize

# 5. Approuver
POST /periodes/1/approve

# 6. Générer bulletins
POST /payroll/periodes/1/generate-all-payslips

# 7. Exporter
GET /payroll/export/periode/1?export_format=excel
```


## Codes de Statut

### Période de Paie
- `DRAFT`: Créée, pas traitée
- `PROCESSING`: Calcul en cours
- `COMPLETED`: Calcul terminé
- `FINALIZED`: Verrouillée
- `APPROVED`: Approuvée

### Alerte
- `PENDING`: En attente
- `ACKNOWLEDGED`: Prise en compte
- `RESOLVED`: Résolue

### Sévérité Alerte
- `HIGH`: Haute
- `MEDIUM`: Moyenne
- `LOW`: Basse

## Types de Retenue
- `PRET`: Prêt
- `AVANCE`: Avance sur salaire
- `SAISIE`: Saisie sur salaire
- `AUTRE`: Autre retenue

## Codes HTTP
- `200`: Succès
- `400`: Requête invalide
- `401`: Non authentifié
- `403`: Non autorisé
- `404`: Non trouvé
- `500`: Erreur serveur

## Headers Requis
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## Exemples de Requêtes

### Créer une Période
```bash
curl -X POST http://localhost:8000/api/paie/periodes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "annee": 2024,
    "mois": 3,
    "date_debut": "2024-03-01",
    "date_fin": "2024-03-31",
    "statut": "DRAFT"
  }'
```

### Créer une Retenue
```bash
curl -X POST http://localhost:8000/api/paie/retenues \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employe_id": 123,
    "type_retenue": "PRET",
    "description": "Prêt bancaire",
    "montant_mensuel": "50000.00",
    "montant_total": "500000.00",
    "date_debut": "2024-03-01",
    "est_active": true
  }'
```

### Obtenir Statistiques
```bash
curl -X GET "http://localhost:8000/api/paie/statistics/dashboard?annee=2024&mois=3" \
  -H "Authorization: Bearer <token>"
```

### Exporter une Période
```bash
curl -X GET "http://localhost:8000/api/paie/payroll/export/periode/1?export_format=excel" \
  -H "Authorization: Bearer <token>" \
  --output periode_mars_2024.xlsx
```

---

**Version**: 1.0
**Dernière mise à jour**: 2024-02-17

