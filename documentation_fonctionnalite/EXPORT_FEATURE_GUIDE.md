# Guide d'Export Avancé - Module Paie

## 📊 Vue d'ensemble

Le module d'export avancé permet d'exporter les données de paie dans différents formats (Excel, CSV) pour faciliter l'analyse, l'archivage et le partage des informations.

## ✨ Fonctionnalités

### 1. Export de Période de Paie (Excel/CSV)

Exporte une période de paie spécifique avec toutes ses données détaillées.

**Format Excel** : Contient 3 feuilles
- **Résumé** : Informations générales de la période
- **Détails Paie** : Détails de chaque employé
- **Retenues** : Retenues actives pour les employés

**Format CSV** : Fichier unique avec les détails de paie

**Endpoint** : `GET /payroll/export/periode/{periode_id}`

**Paramètres** :
- `pe
les Périodes (Excel)

Exporte un résumé de toutes les périodes de paie, optionnellement filtré par année.

**Endpoint** : `GET /payroll/export/all-periodes`

**Paramètres** :
- `annee` (query, optionnel) : Année pour filtrer les périodes

**Exemple** :
```bash
# Toutes les périodes
curl -X GET "http://localhost:8000/api/v1/payroll/export/all-periodes" \
  -H "Authorization: Bearer {token}" \
  --output toutes_periodes.xlsx

# Périodes de 2024
curl -X GET "http://localhost:8000/api/v1/payroll/export/all-periodes?annee=2024" \
  -H "Authorization: Bearer {token}" \
  --output periodes_2024.xlsx
```

### 3. Export des Retenues (CSV)

Exporte les retenues employés, optionnellement filtré par employé.

**Endpoint** : `GET /payroll/export/retenues`

**Paramètres** :
- `employe_id` (query, optionnel) : ID de l'employé pour filtrer

**Exemple** :
```bash
# Toutes les retenues
curl -X GET "http://localhost:8000/api/v1/payroll/export/retenues" \
  -H "Authorization: Bearer {token}" \
  --output retenues.csv

# Retenues d'un employé
curl -X GET "http://localhost:8000/api/v1/payroll/export/retenues?employe_id=123" \
  -H "Authorization: Bearer {token}" \
  --output retenues_emp123.csv
```

## 📋 Structure des Fichiers Exportés

### Excel - Période de Paie

#### Feuille "Résumé"
| Champ | Description |
|-------|-------------|
| Période de Paie | Mois/Année |
| Statut | État de la période |
| Date début | Date de début |
| Date fin | Date de fin |
| Nombre d'employés | Total employés |
| Masse salariale brute | Total brut |
| Total cotisations patronales | Cotisations employeur |
| Total cotisations salariales | Cotisations employé |
| Total net à payer | Total net |

#### Feuille "Détails Paie"
| Colonne | Description |
|---------|-------------|
| ID | ID de l'entrée |
| Employé | Nom complet |
| Matricule | Matricule employé |
| Salaire Base | Salaire de base |
| Ind. Logement | Indemnité logement |
| Ind. Déplacement | Indemnité déplacement |
| Ind. Fonction | Indemnité fonction |
| Allocation Familiale | Allocation familiale |
| Autres Avantages | Autres avantages |
| Salaire Brut | Salaire brut total |
| Cotisations Salariales | Total cotisations |
| Base Imposable | Base pour IRE |
| IRE | Impôt sur le revenu |
| Retenues Diverses | Autres retenues |
| Salaire Net | Salaire net à payer |

#### Feuille "Retenues"
| Colonne | Description |
|---------|-------------|
| ID | ID de la retenue |
| Employé | Nom complet |
| Type | Type de retenue |
| Description | Description |
| Montant Mensuel | Montant par mois |
| Montant Total | Montant total |
| Déjà Déduit | Montant déjà déduit |
| Solde | Solde restant |
| Date Début | Date de début |
| Date Fin | Date de fin |
| Active | Statut actif |
| Récurrente | Retenue récurrente |

### CSV - Période de Paie

Fichier unique avec les colonnes de la feuille "Détails Paie" (voir ci-dessus).

### CSV - Retenues

Fichier avec les colonnes de la feuille "Retenues" (voir ci-dessus).

## 🔐 Permissions Requises

Tous les endpoints d'export nécessitent la permission `payroll.view`.

## 📁 Emplacement des Fichiers

Les fichiers exportés sont sauvegardés dans :
```
media/exports/payroll/
```

Format des noms de fichiers :
- Période : `paie_{annee}_{mois}_{timestamp}.xlsx|csv`
- Toutes périodes : `paie_all_{annee}_{timestamp}.xlsx`
- Retenues : `retenues_{emp_id}_{timestamp}.csv`

## 🎨 Formatage Excel

### Styles Appliqués

- **En-têtes** : Fond bleu (#4472C4), texte blanc, gras, bordures
- **Montants** : Format monétaire avec 2 décimales (#,##0.00)
- **Dates** : Format dd/mm/yyyy
- **Colonnes** : Largeurs auto-ajustées pour lisibilité

## 🔄 Audit

Toutes les opérations d'export sont auditées avec :
- Utilisateur qui a effectué l'export
- Type de ressource exportée
- Format d'export
- Nombre d'enregistrements
- Date et heure

## 💡 Cas d'Usage

### 1. Archivage Mensuel
```bash
# Exporter la paie du mois en Excel
curl -X GET "http://localhost:8000/api/v1/payroll/export/periode/{periode_id}?export_format=excel" \
  -H "Authorization: Bearer {token}" \
  --output archives/paie_2024_01.xlsx
```

### 2. Analyse Annuelle
```bash
# Exporter toutes les périodes de l'année
curl -X GET "http://localhost:8000/api/v1/payroll/export/all-periodes?annee=2024" \
  -H "Authorization: Bearer {token}" \
  --output analyse/periodes_2024.xlsx
```

### 3. Suivi des Retenues
```bash
# Exporter les retenues d'un employé
curl -X GET "http://localhost:8000/api/v1/payroll/export/retenues?employe_id=123" \
  -H "Authorization: Bearer {token}" \
  --output suivi/retenues_emp123.csv
```

### 4. Import dans un Système Comptable
```bash
# Exporter en CSV pour import
curl -X GET "http://localhost:8000/api/v1/payroll/export/periode/{periode_id}?export_format=csv" \
  -H "Authorization: Bearer {token}" \
  --output comptabilite/import_paie.csv
```

## 🛠️ Intégration avec le Frontend

### Exemple React/TypeScript

```typescript
// Service d'export
export const exportPeriode = async (
  periodeId: number,
  format: 'excel' | 'csv'
): Promise<Blob> => {
  const response = await fetch(
    `/api/v1/payroll/export/periode/${periodeId}?export_format=${format}`,
    {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    }
  );

  if (!response.ok) {
    throw new Error('Export failed');
  }

  return response.blob();
};

// Composant bouton d'export
const ExportButton: React.FC<{ periodeId: number }> = ({ periodeId }) => {
  const handleExport = async (format: 'excel' | 'csv') => {
    try {
      const blob = await exportPeriode(periodeId, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `paie_${periodeId}.${format === 'excel' ? 'xlsx' : 'csv'}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  return (
    <div>
      <button onClick={() => handleExport('excel')}>
        Export Excel
      </button>
      <button onClick={() => handleExport('csv')}>
        Export CSV
      </button>
    </div>
  );
};
```

## 🐛 Gestion des Erreurs

### Erreurs Possibles

| Code | Message | Solution |
|------|---------|----------|
| 404 | Period not found | Vérifier l'ID de la période |
| 404 | No periods found | Aucune période à exporter |
| 404 | No deductions found | Aucune retenue à exporter |
| 403 | Permission denied | Vérifier les permissions |
| 500 | Export error | Vérifier les logs serveur |

### Exemple de Gestion d'Erreur

```python
try:
    file_path = await export_service.export_periode_to_excel(periode_id)
except ValueError as e:
    # Période non trouvée
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    # Erreur système
    raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")
```

## 📊 Performance

### Optimisations Implémentées

1. **Chargement Eager** : Utilisation de `selectinload` pour charger les relations
2. **Streaming** : Écriture directe dans les fichiers (pas de buffer mémoire)
3. **Formatage Efficace** : Utilisation de xlsxwriter (plus rapide qu'openpyxl)

### Recommandations

- Pour les grandes périodes (>1000 employés), préférer le format CSV
- Exécuter les exports en tâche de fond pour les très gros volumes
- Nettoyer régulièrement le dossier `media/exports/payroll/`

## 🔮 Améliorations Futures

- [ ] Export PDF multi-pages
- [ ] Export avec graphiques et statistiques
- [ ] Export personnalisé (sélection de colonnes)
- [ ] Export planifié (automatique)
- [ ] Compression ZIP pour exports multiples
- [ ] Export vers cloud storage (S3, Azure Blob)
- [ ] Templates d'export personnalisables

## 📝 Notes Techniques

### Dépendances

```toml
dependencies = [
    "openpyxl>=3.1.2",    # Lecture/écriture Excel
    "xlsxwriter>=3.1.9",  # Écriture Excel optimisée
]
```

### Structure du Code

```
app/paie_app/services/
├── export_service.py          # Service d'export principal
├── salary_calculator.py       # Calcul des salaires
├── period_processor.py        # Traitement des périodes
└── payslip_generator.py       # Génération bulletins PDF
```

### Tests

```bash
# Test d'import
python test_export_service.py

# Tests unitaires (à implémenter)
pytest tests/test_export_service.py -v
```

---

**Date de création** : 2024-02-17
**Version** : 1.0.0
**Status** : ✅ IMPLÉMENTÉ
