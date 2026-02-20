# API Documentation - Module Paie (Payroll)

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Authentification et Permissions](#authentification-et-permissions)
3. [Endpoints Alertes](#endpoints-alertes)
4. [Endpoints Retenues](#endpoints-retenues)
5. [Endpoints Périodes de Paie](#endpoints-périodes-de-paie)
6. [Endpoints Entrées de Paie](#endpoints-entrées-de-paie)
7. [Endpoints Export](#endpoints-export)
8. [Endpoints Bulletins de Paie (PDF)](#endpoints-bulletins-de-paie-pdf)
9. [Endpoints Statistiques](#endpoints-statistiques)
10. [Endpoints Historique des Modifications](#endpoints-historique-des-modifications)
11. [Modèles de Données](#modèles-de-données)
12. [Codes d'Erreur](#codes-derreur)

---

## Vue d'ensemble

L'API du module Paie fournit des endpoints REST pour gérer:
- Les alertes de paie
- Les retenues employés
- Les périodes de paie
- Les entrées de paie (calculs individuels)
- L'export de données (Excel, CSV)
- La génération de bulletins de paie (PDF)
- Les statistiques et rapports
- L'historique des modifications

**Base URL**: `/api/paie`

**Format de réponse**: JSON (sauf exports et PDF)

**Authentification**: Toutes les routes nécessitent un token JWT valide

---

## Authentification et Permissions

### Headers requis
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Permissions par ressource

| Ressource | Permissions disponibles |
|-----------|------------------------|
| alert | view, create, update |
| retenue | view, create, update |
| periode | view, create, update |
| entree | view, update |
| payroll | view |


---

## Endpoints Alertes

### 1. Lister les alertes

**GET** `/alerts`

Liste toutes les alertes de paie avec pagination.

**Permission requise**: `alert.view`

**Paramètres de requête**:
- `skip` (int, optionnel): Nombre d'éléments à ignorer (défaut: 0)
- `limit` (int, optionnel): Nombre maximum d'éléments (défaut: 100)

**Réponse**: `200 OK`
```json
[
  {
    "id": 1,
    "alert_type": "MISSING_DATA",
    "severity": "HIGH",
    "status": "PENDING",
    "title": "Données manquantes",
    "message": "Salaire de base manquant pour l'employé",
    "details": {"field": "salaire_base"},
    "employe_id": 123,
    "periode_paie_id": 45,
    "created_by_id": 1,
    "acknowledged_by_id": null,
    "acknowledged_at": null,
    "resolved_by_id": null,
    "resolved_at": null,
    "email_sent": false,
    "email_sent_at": null,
    "created_at": "2024-02-17T10:00:00",
    "updated_at": "2024-02-17T10:00:00"
  }
]
```

### 2. Créer une alerte

**POST** `/alerts`

Crée une nouvelle alerte de paie.

**Permission requise**: `alert.create`

**Corps de la requête**:
```json
{
  "alert_type": "MISSING_DATA",
  "severity": "HIGH",
  "status": "PENDING",
  "title": "Données manquantes",
  "message": "Salaire de base manquant pour l'employé",
  "details": {"field": "salaire_base"},
  "employe_id": 123,
  "periode_paie_id": 45,
  "created_by_id": 1
}
```

**Réponse**: `200 OK`
```json
{
  "id": 1,
  "alert_type": "MISSING_DATA",
  "severity": "HIGH",
  "status": "PENDING",
  "title": "Données manquantes",
  "message": "Salaire de base manquant pour l'employé",
  "details": {"field": "salaire_base"},
  "employe_id": 123,
  "periode_paie_id": 45,
  "created_by_id": 1,
  "created_at": "2024-02-17T10:00:00",
  "updated_at": "2024-02-17T10:00:00"
}
```

**Note**: Si les notifications sont activées, un email est envoyé automatiquement.


### 3. Obtenir une alerte

**GET** `/alerts/{alert_id}`

Récupère les détails d'une alerte spécifique.

**Permission requise**: `alert.view`

**Paramètres de chemin**:
- `alert_id` (int): ID de l'alerte

**Réponse**: `200 OK` (même structure que la création)

**Erreurs**:
- `404 Not Found`: Alerte non trouvée

### 4. Envoyer une notification manuelle

**POST** `/alerts/{alert_id}/send-notification`

Envoie manuellement une notification email pour une alerte.

**Permission requise**: `alert.update`

**Paramètres de chemin**:
- `alert_id` (int): ID de l'alerte

**Réponse**: `200 OK`
```json
{
  "message": "Notification sent successfully"
}
```

**Erreurs**:
- `404 Not Found`: Alerte non trouvée
- `500 Internal Server Error`: Échec de l'envoi

---

## Endpoints Retenues

### 1. Lister les retenues

**GET** `/retenues`

Liste toutes les retenues employés avec pagination et filtrage.

**Permission requise**: `retenue.view`

**Paramètres de requête**:
- `skip` (int, optionnel): Nombre d'éléments à ignorer (défaut: 0)
- `limit` (int, optionnel): Nombre maximum d'éléments (défaut: 100)
- `employe_id` (int, optionnel): Filtrer par employé

**Réponse**: `200 OK`
```json
[
  {
    "id": 1,
    "employe_id": 123,
    "type_retenue": "PRET",
    "description": "Prêt bancaire",
    "montant_mensuel": "50000.00",
    "montant_total": "500000.00",
    "montant_deja_deduit": "100000.00",
    "date_debut": "2024-01-01",
    "date_fin": "2024-12-31",
    "est_active": true,
    "est_recurrente": true,
    "banque_beneficiaire": "Banque XYZ",
    "compte_beneficiaire": "123456789",
    "cree_par_id": 1,
    "modification_history": [],
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```


### 2. Créer une retenue

**POST** `/retenues`

Crée une nouvelle retenue pour un employé.

**Permission requise**: `retenue.create`

**Corps de la requête**:
```json
{
  "employe_id": 123,
  "type_retenue": "PRET",
  "description": "Prêt bancaire",
  "montant_mensuel": "50000.00",
  "montant_total": "500000.00",
  "montant_deja_deduit": "0.00",
  "date_debut": "2024-01-01",
  "date_fin": "2024-12-31",
  "est_active": true,
  "est_recurrente": true,
  "banque_beneficiaire": "Banque XYZ",
  "compte_beneficiaire": "123456789",
  "cree_par_id": 1
}
```

**Réponse**: `200 OK` (même structure que la liste)

**Note**: Si les notifications sont activées, un email est envoyé automatiquement.

**Erreurs**:
- `400 Bad Request`: Données invalides (ex: montant négatif, dates incohérentes)

---

## Endpoints Périodes de Paie

### 1. Lister les périodes

**GET** `/periodes`

Liste toutes les périodes de paie avec pagination et filtrage.

**Permission requise**: `periode.view`

**Paramètres de requête**:
- `skip` (int, optionnel): Nombre d'éléments à ignorer (défaut: 0)
- `limit` (int, optionnel): Nombre maximum d'éléments (défaut: 100)
- `annee` (int, optionnel): Filtrer par année
- `mois` (int, optionnel): Filtrer par mois (1-12)

**Réponse**: `200 OK`
```json
[
  {
    "id": 1,
    "annee": 2024,
    "mois": 2,
    "date_debut": "2024-02-01",
    "date_fin": "2024-02-29",
    "statut": "APPROVED",
    "traite_par_id": 1,
    "date_traitement": "2024-02-28T10:00:00",
    "approuve_par_id": 2,
    "date_approbation": "2024-02-28T15:00:00",
    "nombre_employes": 50,
    "masse_salariale_brute": "25000000.00",
    "total_cotisations_patronales": "2500000.00",
    "total_cotisations_salariales": "1500000.00",
    "total_net_a_payer": "21000000.00",
    "created_at": "2024-02-01T10:00:00",
    "updated_at": "2024-02-28T15:00:00"
  }
]
```


### 2. Créer une période

**POST** `/periodes`

Crée une nouvelle période de paie.

**Permission requise**: `periode.create`

**Corps de la requête**:
```json
{
  "annee": 2024,
  "mois": 3,
  "date_debut": "2024-03-01",
  "date_fin": "2024-03-31",
  "statut": "DRAFT"
}
```

**Réponse**: `200 OK` (même structure que la liste)

**Erreurs**:
- `400 Bad Request`: Période déjà existante pour ce mois/année

### 3. Traiter une période

**POST** `/periodes/{periode_id}/process`

Lance le calcul de paie pour tous les employés de la période.

**Permission requise**: `periode.update`

**Paramètres de chemin**:
- `periode_id` (int): ID de la période

**Réponse**: `200 OK`
```json
{
  "processed": 50,
  "errors": 0,
  "warnings": 2,
  "total_net": "21000000.00"
}
```

**Note**:
- Change le statut de DRAFT à PROCESSING puis COMPLETED
- Si les notifications sont activées, un email est envoyé
- Crée une entrée de paie pour chaque employé actif

**Erreurs**:
- `400 Bad Request`: Période déjà traitée ou statut invalide
- `404 Not Found`: Période non trouvée

### 4. Finaliser une période

**POST** `/periodes/{periode_id}/finalize`

Finalise une période de paie (verrouille les modifications).

**Permission requise**: `periode.update`

**Paramètres de chemin**:
- `periode_id` (int): ID de la période

**Réponse**: `200 OK`
```json
{
  "message": "Period finalized successfully"
}
```

**Note**: Change le statut de COMPLETED à FINALIZED

**Erreurs**:
- `400 Bad Request`: Période non complétée ou déjà finalisée
- `404 Not Found`: Période non trouvée


### 5. Approuver une période

**POST** `/periodes/{periode_id}/approve`

Approuve une période de paie finalisée.

**Permission requise**: `periode.update`

**Paramètres de chemin**:
- `periode_id` (int): ID de la période

**Réponse**: `200 OK`
```json
{
  "message": "Period approved successfully"
}
```

**Note**:
- Change le statut de FINALIZED à APPROVED
- Si les notifications sont activées, un email est envoyé

**Erreurs**:
- `400 Bad Request`: Période non finalisée ou déjà approuvée
- `404 Not Found`: Période non trouvée

---

## Endpoints Entrées de Paie

### 1. Lister les entrées

**GET** `/entrees`

Liste toutes les entrées de paie avec pagination et filtrage.

**Permission requise**: `entree.view`

**Paramètres de requête**:
- `skip` (int, optionnel): Nombre d'éléments à ignorer (défaut: 0)
- `limit` (int, optionnel): Nombre maximum d'éléments (défaut: 100)
- `periode_id` (int, optionnel): Filtrer par période

**Réponse**: `200 OK`
```json
[
  {
    "id": 1,
    "employe_id": 123,
    "periode_paie_id": 45,
    "contrat_reference": "CTR-2024-001",
    "salaire_base": "500000.00",
    "indemnite_logement": "100000.00",
    "indemnite_deplacement": "50000.00",
    "indemnite_fonction": "75000.00",
    "allocation_familiale": "25000.00",
    "autres_avantages": "0.00",
    "salaire_brut": "750000.00",
    "cotisations_patronales": "75000.00",
    "cotisations_salariales": "45000.00",
    "retenues_diverses": "50000.00",
    "total_charge_salariale": "825000.00",
    "base_imposable": "655000.00",
    "salaire_net": "605000.00",
    "payslip_generated": true,
    "payslip_file": "media/payslips/2024/02/payslip_123_45.pdf",
    "payslip_generated_at": "2024-02-28T16:00:00",
    "is_validated": true,
    "validation_errors": null,
    "calculated_by_id": 1,
    "calculated_at": "2024-02-28T10:00:00",
    "validated_by_id": 1,
    "validated_at": "2024-02-28T10:30:00",
    "modification_history": [],
    "created_at": "2024-02-28T10:00:00",
    "updated_at": "2024-02-28T16:00:00"
  }
]
```


### 2. Recalculer une entrée

**POST** `/entrees/{entree_id}/calculate`

Recalcule le salaire pour une entrée de paie spécifique.

**Permission requise**: `entree.update`

**Paramètres de chemin**:
- `entree_id` (int): ID de l'entrée

**Réponse**: `200 OK` (même structure que la liste)

**Note**: Recalcule tous les montants (brut, cotisations, net) basés sur les données actuelles du contrat

**Erreurs**:
- `400 Bad Request`: Erreur de calcul (données manquantes)
- `404 Not Found`: Entrée non trouvée

---

## Endpoints Export

### 1. Exporter une période

**GET** `/payroll/export/periode/{periode_id}`

Exporte les données d'une période de paie en Excel ou CSV.

**Permission requise**: `payroll.view`

**Paramètres de chemin**:
- `periode_id` (int): ID de la période

**Paramètres de requête**:
- `export_format` (string): Format d'export - `excel` ou `csv` (défaut: `excel`)

**Réponse**: `200 OK`
- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (Excel)
- **Content-Type**: `text/csv` (CSV)
- Fichier téléchargeable

**Format Excel** (3 feuilles):
1. **Résumé**: Statistiques globales de la période
2. **Détails Paie**: Toutes les entrées de paie
3. **Retenues**: Retenues appliquées

**Format CSV**: Fichier unique avec les entrées de paie

**Erreurs**:
- `404 Not Found`: Période non trouvée
- `500 Internal Server Error`: Erreur de génération

### 2. Exporter toutes les périodes

**GET** `/payroll/export/all-periodes`

Exporte toutes les périodes de paie en Excel.

**Permission requise**: `payroll.view`

**Paramètres de requête**:
- `annee` (int, optionnel): Filtrer par année

**Réponse**: `200 OK`
- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Fichier Excel multi-feuilles (une feuille par période)

**Erreurs**:
- `404 Not Found`: Aucune période trouvée
- `500 Internal Server Error`: Erreur de génération


### 3. Exporter les retenues

**GET** `/payroll/export/retenues`

Exporte les retenues employés en CSV.

**Permission requise**: `payroll.view`

**Paramètres de requête**:
- `employe_id` (int, optionnel): Filtrer par employé

**Réponse**: `200 OK`
- **Content-Type**: `text/csv`
- Fichier CSV avec toutes les retenues

**Erreurs**:
- `404 Not Found`: Aucune retenue trouvée
- `500 Internal Server Error`: Erreur de génération

### 4. Export générique (Déprécié)

**GET** `/payroll/export`

Endpoint déprécié. Utiliser les endpoints spécifiques ci-dessus.

**Permission requise**: `payroll.view`

**Réponse**: `200 OK`
```json
{
  "message": "Payroll export excel requested",
  "count": 12,
  "format": "excel",
  "note": "This endpoint is deprecated. Use /export/periode/{id} or /export/all-periodes"
}
```

---

## Endpoints Bulletins de Paie (PDF)

### 1. Générer un bulletin

**POST** `/payroll/entrees/{entree_id}/generate-payslip`

Génère un bulletin de paie PDF pour une entrée spécifique.

**Permission requise**: `entree.view`

**Paramètres de chemin**:
- `entree_id` (int): ID de l'entrée de paie

**Réponse**: `200 OK`
```json
{
  "message": "Payslip generated successfully",
  "file_path": "media/payslips/2024/02/payslip_123_45.pdf",
  "entree_id": 1
}
```

**Note**:
- Génère un PDF formaté avec toutes les informations de paie
- Si les notifications sont activées, un email est envoyé à l'employé
- Le fichier est sauvegardé dans `media/payslips/{annee}/{mois}/`

**Erreurs**:
- `400 Bad Request`: Données manquantes pour la génération
- `404 Not Found`: Entrée non trouvée
- `500 Internal Server Error`: Erreur de génération PDF


### 2. Télécharger un bulletin

**GET** `/payroll/entrees/{entree_id}/download-payslip`

Télécharge le bulletin de paie PDF d'une entrée.

**Permission requise**: `entree.view`

**Paramètres de chemin**:
- `entree_id` (int): ID de l'entrée de paie

**Réponse**: `200 OK`
- **Content-Type**: `application/pdf`
- Fichier PDF téléchargeable

**Erreurs**:
- `404 Not Found`: Entrée non trouvée, bulletin non généré, ou fichier manquant

### 3. Générer tous les bulletins d'une période

**POST** `/payroll/periodes/{periode_id}/generate-all-payslips`

Génère les bulletins de paie PDF pour toutes les entrées d'une période.

**Permission requise**: `periode.view`

**Paramètres de chemin**:
- `periode_id` (int): ID de la période

**Réponse**: `200 OK`
```json
{
  "message": "Generated 50 payslips successfully",
  "count": 50,
  "file_paths": [
    "media/payslips/2024/02/payslip_123_45.pdf",
    "media/payslips/2024/02/payslip_124_45.pdf"
  ],
  "periode_id": 45
}
```

**Note**: Génère un bulletin pour chaque entrée de paie de la période

**Erreurs**:
- `400 Bad Request`: Période invalide ou données manquantes
- `404 Not Found`: Période non trouvée
- `500 Internal Server Error`: Erreur de génération

---

## Endpoints Statistiques

### 1. Résumé d'une période

**GET** `/statistics/periode/{periode_id}/summary`

Obtient un résumé complet des statistiques d'une période.

**Permission requise**: `payroll.view`

**Paramètres de chemin**:
- `periode_id` (int): ID de la période

**Réponse**: `200 OK`
```json
{
  "periode_id": 45,
  "annee": 2024,
  "mois": 2,
  "statut": "APPROVED",
  "nombre_employes": 50,
  "masse_salariale_brute": "25000000.00",
  "total_cotisations_patronales": "2500000.00",
  "total_cotisations_salariales": "1500000.00",
  "total_retenues": "500000.00",
  "total_net_a_payer": "21000000.00",
  "cout_total_employeur": "27500000.00",
  "salaire_moyen": "500000.00",
  "salaire_median": "480000.00",
  "salaire_min": "200000.00",
  "salaire_max": "1500000.00"
}
```

**Erreurs**:
- `404 Not Found`: Période non trouvée


### 2. Résumé annuel

**GET** `/statistics/annual/{annee}/summary`

Obtient un résumé annuel avec données mensuelles.

**Permission requise**: `payroll.view`

**Paramètres de chemin**:
- `annee` (int): Année

**Réponse**: `200 OK`
```json
{
  "annee": 2024,
  "nombre_periodes": 12,
  "nombre_employes_moyen": 48,
  "masse_salariale_annuelle": "300000000.00",
  "total_cotisations_patronales": "30000000.00",
  "total_cotisations_salariales": "18000000.00",
  "total_net_paye": "252000000.00",
  "cout_total_employeur": "330000000.00",
  "donnees_mensuelles": [
    {
      "mois": 1,
      "nombre_employes": 45,
      "masse_salariale": "24000000.00",
      "net_paye": "20500000.00"
    }
  ]
}
```

**Erreurs**:
- `404 Not Found`: Aucune période trouvée pour cette année

### 3. Historique employé

**GET** `/statistics/employee/{employe_id}/history`

Obtient l'historique de paie d'un employé.

**Permission requise**: `payroll.view`

**Paramètres de chemin**:
- `employe_id` (int): ID de l'employé

**Paramètres de requête**:
- `annee` (int, optionnel): Filtrer par année
- `limit` (int, optionnel): Nombre de mois (défaut: 12, max: 24)

**Réponse**: `200 OK`
```json
{
  "employe_id": 123,
  "nombre_periodes": 12,
  "salaire_brut_total": "9000000.00",
  "salaire_net_total": "7500000.00",
  "cotisations_totales": "900000.00",
  "retenues_totales": "600000.00",
  "salaire_brut_moyen": "750000.00",
  "salaire_net_moyen": "625000.00",
  "historique": [
    {
      "periode_id": 45,
      "annee": 2024,
      "mois": 2,
      "salaire_brut": "750000.00",
      "salaire_net": "625000.00",
      "cotisations": "75000.00",
      "retenues": "50000.00"
    }
  ]
}
```

**Erreurs**:
- `404 Not Found`: Employé non trouvé

 "CALCULATION_ERROR": 4,
    "VALIDATION_ERROR": 5
  },
  "alertes_recentes": [
    {
      "id": 1,
      "alert_type": "MISSING_DATA",
      "severity": "HIGH",
      "status": "PENDING",
      "title": "Données manquantes",
      "created_at": "2024-02-17T10:00:00"
    }
  ]
}
```

lertes de paie.

**Permission requise**: `alert.view`

**Paramètres de requête**:
- `periode_id` (int, optionnel): Filtrer par période
- `severity` (string, optionnel): Filtrer par sévérité
- `status` (string, optionnel): Filtrer par statut

**Réponse**: `200 OK`
```json
{
  "total_alertes": 15,
  "alertes_par_severite": {
    "HIGH": 5,
    "MEDIUM": 7,
    "LOW": 3
  },
  "alertes_par_statut": {
    "PENDING": 8,
    "ACKNOWLEDGED": 5,
    "RESOLVED": 2
  },
  "alertes_par_type": {
    "MISSING_DATA": 6,
   "count": 15,
      "montant_total": "7500000.00",
      "montant_restant": "4500000.00"
    },
    "AVANCE": {
      "count": 10,
      "montant_total": "5000000.00",
      "montant_restant": "3000000.00"
    }
  },
  "retenues": [
    {
      "id": 1,
      "employe_id": 123,
      "type_retenue": "PRET",
      "montant_mensuel": "50000.00",
      "montant_restant": "300000.00",
      "mois_restants": 6
    }
  ]
}
```

### 5. Résumé des alertes

**GET** `/statistics/alerts/summary`

Obtient un résumé des a
### 4. Résumé des retenues

**GET** `/statistics/deductions/summary`

Obtient un résumé des retenues actives.

**Permission requise**: `retenue.view`

**Paramètres de requête**:
- `employe_id` (int, optionnel): Filtrer par employé
- `type_retenue` (string, optionnel): Filtrer par type

**Réponse**: `200 OK`
```json
{
  "nombre_retenues_actives": 25,
  "montant_total_a_deduire": "12500000.00",
  "montant_deja_deduit": "5000000.00",
  "montant_restant": "7500000.00",
  "retenues_par_type": {
    "PRET": {

### 4. Résumé des retenues

**GET** `/statistics/deductions/summary`

Obtient un résumé des retenues actives.

**Permission requise**: `retenue.view`

**Paramètres de requête**:
- `employe_id` (int, optionnel): Filtrer par employé
- `type_retenue` (string, optionnel): Filtrer par type

**Réponse**: `200 OK`
```json
{
  "nombre_retenues_actives": 25,
  "montant_total_a_deduire": "12500000.00",
  "montant_deja_deduit": "5000000.00",
  "montant_restant": "7500000.00",
  "retenues_par_type": {
    "PRET": {"count": 15, "montant_total": "7500000.00"}
  }
}
```

### 5. Résumé des alertes

**GET** `/statistics/alerts/summary`

Obtient un résumé des alertes de paie.

**Permission requise**: `alert.view`

**Paramètres de requête**:
- `periode_id` (int, optionnel): Filtrer par période
- `severity` (string, optionnel): Filtrer par sévérité
- `status` (string, optionnel): Filtrer par statut

**Réponse**: `200 OK`
```json
{
  "total_alertes": 15,
  "alertes_par_severite": {"HIGH": 5, "MEDIUM": 7, "LOW": 3},
  "alertes_par_statut": {"PENDING": 8, "ACKNOWLEDGED": 5}
}
```


### 6. Analyse comparative

**GET** `/statistics/comparative/{annee}/{mois}`

Compare une période avec la période précédente ou le même mois l'année précédente.

**Permission requise**: `payroll.view`

**Paramètres de chemin**:
- `annee` (int): Année
- `mois` (int): Mois (1-12)

**Paramètres de requête**:
- `compare_to_previous` (bool): `true` pour mois précédent, `false` pour même mois année précédente (défaut: `true`)

**Réponse**: `200 OK`
```json
{
  "periode_actuelle": {
    "annee": 2024,
    "mois": 2,
    "nombre_employes": 50,
    "masse_salariale": "25000000.00",
    "net_paye": "21000000.00"
  },
  "periode_comparaison": {
    "annee": 2024,
    "mois": 1,
    "nombre_employes": 48,
    "masse_salariale": "24000000.00",
    "net_paye": "20000000.00"
  },
  "variations": {
    "nombre_employes": "+2 (+4.17%)",
    "masse_salariale": "+1000000.00 (+4.17%)",
    "net_paye": "+1000000.00 (+5.00%)"
  }
}
```

**Erreurs**:
- `404 Not Found`: Période actuelle ou de comparaison non trouvée

### 7. Top salaires

**GET** `/statistics/top-earners`

Obtient les employés avec les salaires les plus élevés.

**Permission requise**: `payroll.view`

**Paramètres de requête**:
- `periode_id` (int, optionnel): Filtrer par période
- `annee` (int, optionnel): Filtrer par année
- `limit` (int, optionnel): Nombre de résultats (défaut: 10, max: 50)

**Note**: `periode_id` ou `annee` doit être fourni

**Réponse**: `200 OK`
```json
{
  "periode_id": 45,
  "annee": 2024,
  "top_earners": [
    {
      "employe_id": 123,
      "nom_complet": "Jean Dupont",
      "salaire_brut": "1500000.00",
      "salaire_net": "1250000.00",
      "rang": 1
    }
  ]
}
```

**Erreurs**:
- `400 Bad Request`: Ni periode_id ni annee fourni


### 8. Tableau de bord

**GET** `/statistics/dashboard`

Obtient un résumé complet pour le tableau de bord.

**Permission requise**: `payroll.view`

**Paramètres de requête**:
- `annee` (int, optionnel): Année (défaut: année actuelle)
- `mois` (int, optionnel): Mois (défaut: mois actuel)

**Réponse**: `200 OK`
```json
{
  "periode_actuelle": {
    "annee": 2024,
    "mois": 2,
    "statut": "APPROVED",
    "nombre_employes": 50,
    "masse_salariale": "25000000.00",
    "net_paye": "21000000.00"
  },
  "statistiques_annuelles": {
    "nombre_periodes": 2,
    "masse_salariale_ytd": "49000000.00",
    "net_paye_ytd": "41000000.00"
  },
  "alertes": {
    "total": 15,
    "pending": 8,
    "high_severity": 5
  },
  "retenues": {
    "actives": 25,
    "montant_restant": "7500000.00"
  },
  "top_5_earners": []
}
```

---

## Endpoints Historique des Modifications

### 1. Historique d'une entrée de paie

**GET** `/history/entrees/{entree_id}`

Obtient l'historique complet des modifications d'une entrée de paie.

**Permission requise**: `entree.view`

**Paramètres de chemin**:
- `entree_id` (int): ID de l'entrée

**Réponse**: `200 OK`
```json
{
  "resource_type": "entree_paie",
  "resource_id": 1,
  "total_modifications": 3,
  "history": [
    {
      "timestamp": "2024-02-28T10:00:00",
      "user_id": 1,
      "user_name": "Admin User",
      "user_email": "admin@example.com",
      "action": "CREATE",
      "reason": "Création automatique lors du traitement de la période",
      "changes": {}
    },
    {
      "timestamp": "2024-02-28T11:00:00",
      "user_id": 2,
      "user_name": "HR Manager",
      "user_email": "hr@example.com",
      "action": "UPDATE",
      "reason": "Correction du salaire de base",
      "changes": {
        "salaire_base": {
          "old": "500000.00",
          "new": "550000.00"
        }
      }
    }
  ]
}
```

**Erreurs**:
- `404 Not Found`: Entrée non trouvée



### 2. Historique d'une retenue

**GET** `/history/retenues/{retenue_id}`

Obtient l'historique complet des modifications d'une retenue.

**Permission requise**: `retenue.view`

**Paramètres de chemin**:
- `retenue_id` (int): ID de la retenue

**Réponse**: `200 OK`
```json
{
  "resource_type": "retenue_employe",
  "resource_id": 1,
  "total_modifications": 2,
  "history": [
    {
      "timestamp": "2024-01-01T10:00:00",
      "user_id": 1,
      "user_name": "Admin User",
      "user_email": "admin@example.com",
      "action": "CREATE",
      "reason": "Création de la retenue",
      "changes": {}
    },
    {
      "timestamp": "2024-02-01T10:00:00",
      "user_id": 1,
      "user_name": "System",
      "user_email": "system@example.com",
      "action": "APPLY",
      "reason": "Application automatique lors du traitement de la période",
      "changes": {
        "montant_deja_deduit": {
          "old": "50000.00",
          "new": "100000.00"
        }
      }
    }
  ]
}
```

**Erreurs**:
- `404 Not Found`: Retenue non trouvée

---

## Modèles de Données

### Alert

| Champ | Type | Description |
|-------|------|-------------|
| id | int | Identifiant unique |
| alert_type | string | Type d'alerte (MISSING_DATA, CALCULATION_ERROR, etc.) |
| severity | string | Sévérité (HIGH, MEDIUM, LOW) |
| status | string | Statut (PENDING, ACKNOWLEDGED, RESOLVED) |
| title | string | Titre de l'alerte |
| message | string | Message détaillé |
| details | object | Détails supplémentaires (JSON) |
| employe_id | int | ID de l'employé concerné (optionnel) |
| periode_paie_id | int | ID de la période concernée (optionnel) |
| created_by_id | int | ID du créateur |
| acknowledged_by_id | int | ID de l'utilisateur qui a pris connaissance |
| acknowledged_at | datetime | Date de prise de connaissance |
| resolved_by_id | int | ID de l'utilisateur qui a résolu |
| resolved_at | datetime | Date de résolution |
| email_sent | bool | Email envoyé |
| email_sent_at | datetime | Date d'envoi de l'email |
| created_at | datetime | Date de création |
| updated_at | datetime | Date de mise à jour |


### RetenueEmploye

| Champ | Type | Description |
|-------|------|-------------|
| id | int | Identifiant unique |
| employe_id | int | ID de l'employé |
| type_retenue | string | Type (PRET, AVANCE, SAISIE, AUTRE) |
| description | string | Description de la retenue |
| montant_mensuel | decimal | Montant à déduire chaque mois |
| montant_total | decimal | Montant total de la retenue |
| montant_deja_deduit | decimal | Montant déjà déduit |
| date_debut | date | Date de début |
| date_fin | date | Date de fin (optionnel) |
| est_active | bool | Retenue active |
| est_recurrente | bool | Retenue récurrente |
| banque_beneficiaire | string | Banque bénéficiaire (optionnel) |
| compte_beneficiaire | string | Compte bénéficiaire (optionnel) |
| cree_par_id | int | ID du créateur |
| modification_history | object | Historique des modifications (JSON) |
| created_at | datetime | Date de création |
| updated_at | datetime | Date de mise à jour |

### PeriodePaie

| Champ | Type | Description |
|-------|------|-------------|
| id | int | Identifiant unique |
| annee | int | Année |
| mois | int | Mois (1-12) |
| date_debut | date | Date de début |
| date_fin | date | Date de fin |
| statut | string | Statut (DRAFT, PROCESSING, COMPLETED, FINALIZED, APPROVED) |
| traite_par_id | int | ID de l'utilisateur qui a traité |
| date_traitement | datetime | Date de traitement |
| approuve_par_id | int | ID de l'utilisateur qui a approuvé |
| date_approbation | datetime | Date d'approbation |
| nombre_employes | int | Nombre d'employés |
| masse_salariale_brute | decimal | Masse salariale brute totale |
| total_cotisations_patronales | decimal | Total cotisations patronales |
| total_cotisations_salariales | decimal | Total cotisations salariales |
| total_net_a_payer | decimal | Total net à payer |
| created_at | datetime | Date de création |
| updated_at | datetime | Date de mise à jour |


### EntreePaie

| Champ | Type | Description |
|-------|------|-------------|
| id | int | Identifiant unique |
| employe_id | int | ID de l'employé |
| periode_paie_id | int | ID de la période |
| contrat_reference | string | Référence du contrat |
| salaire_base | decimal | Salaire de base |
| indemnite_logement | decimal | Indemnité de logement |
| indemnite_deplacement | decimal | Indemnité de déplacement |
| indemnite_fonction | decimal | Indemnité de fonction |
| allocation_familiale | decimal | Allocation familiale |
| autres_avantages | decimal | Autres avantages |
| salaire_brut | decimal | Salaire brut calculé |
| cotisations_patronales | decimal | Cotisations patronales |
| cotisations_salariales | decimal | Cotisations salariales |
| retenues_diverses | decimal | Retenues diverses |
| total_charge_salariale | decimal | Charge salariale totale |
| base_imposable | decimal | Base imposable |
| salaire_net | decimal | Salaire net |
| payslip_generated | bool | Bulletin généré |
| payslip_file | string | Chemin du fichier PDF |
| payslip_generated_at | datetime | Date de génération du bulletin |
| is_validated | bool | Entrée validée |
| validation_errors | object | Erreurs de validation (JSON) |
| calculated_by_id | int | ID de l'utilisateur qui a calculé |
| calculated_at | datetime | Date de calcul |
| validated_by_id | int | ID de l'utilisateur qui a validé |
| validated_at | datetime | Date de validation |
| modification_history | object | Historique des modifications (JSON) |
| created_at | datetime | Date de création |
| updated_at | datetime | Date de mise à jour |

---

## Codes d'Erreur

### Codes HTTP

| Code | Description |
|------|-------------|
| 200 | Succès |
| 400 | Requête invalide (données manquantes ou incorrectes) |
| 401 | Non authentifié (token manquant ou invalide) |
| 403 | Non autorisé (permission manquante) |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur interne |



### Messages d'Erreur Courants

#### Erreurs de Validation (400)
```json
{
  "detail": "Période déjà existante pour ce mois/année"
}
```

```json
{
  "detail": "Période non complétée ou déjà finalisée"
}
```

```json
{
  "detail": "Données manquantes pour la génération"
}
```

#### Erreurs de Ressource (404)
```json
{
  "detail": "Alert not found"
}
```

```json
{
  "detail": "Période non trouvée"
}
```

```json
{
  "detail": "Payslip not generated yet. Please generate it first."
}
```

#### Erreurs de Permission (403)
```json
{
  "detail": "Permission denied: alert.view required"
}
```

#### Erreurs Serveur (500)
```json
{
  "detail": "Error generating payslip: [error details]"
}
```

---

## Exemples d'Utilisation

### Workflow Complet de Traitement de Paie

#### 1. Créer une période
```bash
POST /api/paie/periodes
{
  "annee": 2024,
  "mois": 3,
  "date_debut": "2024-03-01",
  "date_fin": "2024-03-31",
  "statut": "DRAFT"
}
```

#### 2. Traiter la période (calcul pour tous les employés)
```bash
POST /api/paie/periodes/1/process
```

#### 3. Vérifier les alertes
```bash
GET /api/paie/alerts?periode_id=1
```

#### 4. Recalculer une entrée si nécessaire
```bash
POST /api/paie/entrees/123/calculate
```

#### 5. Finaliser la période
```bash
POST /api/paie/periodes/1/finalize
```

#### 6. Approuver la période
```bash
POST /api/paie/periodes/1/approve
```

#### 7. Générer tous les bulletins
```bash
POST /api/paie/payroll/periodes/1/generate-all-payslips
```

#### 8. Exporter les données
```bash
GET /api/paie/payroll/export/periode/1?export_format=excel
```


### Gestion des Retenues

#### 1. Créer une retenue
```bash
POST /api/paie/retenues
{
  "employe_id": 123,
  "type_retenue": "PRET",
  "description": "Prêt bancaire",
  "montant_mensuel": "50000.00",
  "montant_total": "500000.00",
  "date_debut": "2024-03-01",
  "date_fin": "2024-12-31",
  "est_active": true,
  "est_recurrente": true
}
```

#### 2. Consulter les retenues d'un employé
```bash
GET /api/paie/retenues?employe_id=123
```

#### 3. Voir l'historique d'une retenue
```bash
GET /api/paie/history/retenues/1
```

### Consultation des Statistiques

#### 1. Tableau de bord du mois en cours
```bash
GET /api/paie/statistics/dashboard
```

#### 2. Résumé annuel
```bash
GET /api/paie/statistics/annual/2024/summary
```

#### 3. Historique d'un employé
```bash
GET /api/paie/statistics/employee/123/history?annee=2024
```

#### 4. Analyse comparative
```bash
GET /api/paie/statistics/comparative/2024/3?compare_to_previous=true
```

#### 5. Top 10 des salaires
```bash
GET /api/paie/statistics/top-earners?annee=2024&limit=10
```

---

## Notes Techniques

### Calcul du Salaire

Le calcul du salaire suit cette logique:

1. **Salaire Brut** = salaire_base + indemnite_logement + indemnite_deplacement + indemnite_fonction + allocation_familiale + autres_avantages

2. **Cotisations Patronales**:
   - INSS Patronal: salaire_brut × 5%
   - Assurance Patronale: salaire_brut × assurance_patronale%
   - FPC Patronal: salaire_brut × fpc_patronale%

3. **Cotisations Salariales**:
   - INSS Employé: salaire_brut × 3.5%
   - Assurance Salariale: salaire_brut × assurance_salariale%
   - FPC Employé: salaire_brut × fpc_salariale%

4. **Base Imposable** = salaire_brut - indemnite_logement - indemnite_deplacement - indemnite_fonction - cotisations_salariales

5. **IRE (Impôt sur le Revenu)**:
   - 0 - 150,000 FC: 0%
   - 150,001 - 300,000 FC: 20%
   - 300,001+ FC: 30%

6. **Salaire Net** = salaire_brut - cotisations_salariales - ire - retenues_diverses


### Workflow des Statuts de Période

```
DRAFT → PROCESSING → COMPLETED → FINALIZED → APPROVED
```

- **DRAFT**: Période créée, pas encore traitée
- **PROCESSING**: Calcul en cours
- **COMPLETED**: Calcul terminé, modifications possibles
- **FINALIZED**: Période verrouillée, pas de modifications
- **APPROVED**: Période approuvée, prête pour paiement

### Notifications Automatiques

Les notifications par email sont envoyées automatiquement (si activées) pour:
- Création d'alertes
- Création de retenues
- Traitement de périodes
- Approbation de périodes
- Génération de bulletins de paie

Configuration dans `.env`:
```
NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@company.com
SMTP_TLS=true
```

### Audit et Traçabilité

Toutes les actions importantes sont automatiquement auditées:
- Création, modification, suppression de ressources
- Traitement et approbation de périodes
- Génération de bulletins et exports
- Envoi de notifications

L'historique des modifications est stocké dans le champ `modification_history` (JSON) pour:
- Entrées de paie
- Retenues employés

### Formats d'Export

#### Excel (.xlsx)
- Multi-feuilles avec formatage professionnel
- Couleurs, bordures, formats monétaires
- Idéal pour analyse et présentation

#### CSV (.csv)
- Fichier simple pour import dans d'autres systèmes
- Compatible avec Excel, Google Sheets, etc.

#### PDF
- Bulletins de paie formatés
- Prêts pour impression et distribution

---

## Support et Contact

Pour toute question ou problème concernant l'API:
- Documentation technique: Voir les fichiers `*_GUIDE.md` dans le projet
- Référence rapide: Voir les fichiers `*_QUICK_REFERENCE.md`

---

**Version**: 1.0
**Dernière mise à jour**: 2024-02-17
**Statut**: ✅ Complet et Opérationnel

