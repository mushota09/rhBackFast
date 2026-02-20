# Statistics API - Quick Reference

## Base URL
```
/statistics
```

## Endpoints Overview

| Endpoint | Method | Permission | Description |
|----------|--------|------------|-------------|
| `/periode/{id}/summary` | GET | payroll.view | Résumé d'une période |
| `/annual/{annee}/summary` | GET | payroll.view | Résumé annuel |
| `/employee/{id}/history` | GET | payroll.view | Historique employé |
| `/deductions/summary` | GET | retenue.view | Résumé des retenues |
| `/alerts/summary` | GET | alert.view | Résumé des alertes |
| `/comparative/{annee}/{mois}` | GET | payroll.view | Analyse comparative |
| `/top-earners` | GET | payroll.view | Top salaires |
| `/dashboard` | GET | payroll.view | Tableau de bord |

## Quick Examples

### 1. Résumé d'une Période
```bash
GET /statistics/periode/1/summary
```
**Retourne:** Statistiques complètes pour la période (masse salariale, cotisations, moyennes)

### 2. Résumé Annuel
```bash
GET /statistics/annual/2024/summary
```
**Retourne:** Totaux annuels et données mensuelles

### 3. Historique Employé
```bash
GET /statistics/employee/123/history?annee=2024&limit=12
```
**Retourne:** Historique de paie sur 12 mois

### 4. Résumé des Retenues
```bash
GET /statistics/deductions/summary?employe_id=123
```
**Retourne:** Retenues actives, montants mensuels, soldes restants

### 5. Résumé des Alertes
```bash
GET /statistics/alerts/summary?status=ACTIVE
```
**Retourne:** Nombre d'alertes par sévérité, statut, type

### 6. Analyse Comparative
```bash
GET /statistics/comparative/2024/2?compare_to_previous=true
```
**Retourne:** Comparaison avec le mois précédent (différences absolues et %)

### 7. Top Salaires
```bash
# Par période
GET /statistics/top-earners?periode_id=1&limit=10

# Par année
GET /statistics/top-earners?annee=2024&limit=10
```
**Retourne:** Liste des employés avec les salaires les plus élevés

### 8. Tableau de Bord
```bash
GET /statistics/dashboard?annee=2024&mois=2
```
**Retourne:** Vue d'ensemble complète (période actuelle, alertes, retenues, top 5, résumé annuel)

## Données Retournées

### Résumé de Période
```json
{
  "periode_i
e_mensuelle_brute": 125000.00,
  "donnees_mensuelles": [...]
}
```

### Analyse Comparative
```json
{
  "periode_actuelle": {...},
  "periode_comparaison": {...},
  "differences": {
    "masse_salariale_brute": {
      "valeur": 5000.00,
      "pourcentage": 4.17
    }
  }
}
```

## Cas d'Usage

### 1. Tableau de Bord de Gestion
```bash
GET /statistics/dashboard
```
Affiche une vue d'ensemble complète pour la direction.

### 2. Rapport Mensuel
```bash
GET /statistics/periode/{periode_id}/summary
```
Génère un rapport détaillé pour une période spécifique.

### 3. Rapport Annuel
```bash
GET /statistics/annual/2024/summary
```
Prépare les données pour les rapports comptables annuels.

### 4. Suivi Employé
```bash
GET /statistics/employee/{employe_id}/history
```
Consulte l'historique de paie pour les évaluations de performance.

### 5. Analyse de Tendances
```bash
GET /statistics/comparative/2024/2?compare_to_previous=false
```
Compare avec le même mois de l'année précédente pour identifier les tendances.

### 6. Gestion des Retenues
```bash
GET /statistics/deductions/summary
```
Surveille les retenues actives et les soldes restants.

### 7. Surveillance des Alertes
```bash
GET /statistics/alerts/summary?severity=HIGH
```
Identifie les alertes critiques nécessitant une attention immédiate.

### 8. Analyse de Rémunération
```bash
GET /statistics/top-earners?annee=2024&limit=20
```
Analyse la distribution des salaires et identifie les hauts salaires.

## Filtres et Paramètres

### Paramètres Communs
- `annee`: Année (YYYY)
- `mois`: Mois (1-12)
- `limit`: Nombre maximum de résultats
- `employe_id`: ID de l'employé
- `periode_id`: ID de la période

### Filtres Spécifiques

#### Historique Employé
- `annee`: Filtrer par année
- `limit`: Nombre de périodes (1-24, défaut: 12)

#### Résumé des Retenues
- `employe_id`: Filtrer par employé
- `type_retenue`: Filtrer par type (PRET, AVANCE, etc.)

#### Résumé des Alertes
- `periode_id`: Filtrer par période
- `severity`: Filtrer par sévérité (HIGH, MEDIUM, LOW)
- `status`: Filtrer par statut (ACTIVE, RESOLVED)

#### Analyse Comparative
- `compare_to_previous`: true = mois précédent, false = même mois année précédente

#### Top Salaires
- `periode_id` OU `annee`: Période ou année (l'un des deux requis)
- `limit`: Nombre de résultats (1-50, défaut: 10)

#### Tableau de Bord
- `annee`: Année (défaut: année actuelle)
- `mois`: Mois (défaut: mois actuel)

## Codes de Réponse

- **200 OK**: Succès
- **400 Bad Request**: Paramètres invalides
- **403 Forbidden**: Permission insuffisante
- **404 Not Found**: Ressource non trouvée
- **500 Internal Server Error**: Erreur serveur

## Permissions Requises

- **payroll.view**: Statistiques générales de paie
- **retenue.view**: Statistiques des retenues
- **alert.view**: Statistiques des alertes

## Notes Importantes

1. Toutes les requêtes nécessitent un token d'authentification valide
2. Les montants sont retournés en format décimal (2 décimales)
3. Les dates sont au format ISO 8601 (YYYY-MM-DD)
4. Les pourcentages sont arrondis à 2 décimales
5. Les résultats sont triés par pertinence (dates décroissantes, montants décroissants)

## Performance

- Les requêtes sont optimisées avec des jointures SQL
- Utilisez les filtres pour réduire la quantité de données
- Le paramètre `limit` permet de contrôler la taille des résultats
- Considérez la mise en cache pour les statistiques fréquemment consultées

## Audit

Toutes les consultations de statistiques sont automatiquement auditées via le middleware d'audit existant.

---

Pour plus de détails, consultez `STATISTICS_IMPLEMENTATION.md`
