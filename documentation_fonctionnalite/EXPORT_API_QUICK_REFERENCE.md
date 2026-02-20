# Export API - Référence Rapide

## 🚀 Endpoints Disponibles

### 1. Exporter une Période de Paie

```http
GET /api/v1/payroll/export/periode/{periode_id}?export_format={format}
```

**Paramètres** :
- `periode_id` (path, requis) : ID de la période
- `export_format` (query, optionnel) : `excel` ou `csv` (défaut: `excel`)

**Réponse** : Fichier téléchargeable

**Exemple cURL** :
```bash
curl -X GET "http://localhost:8000/api/v1/payroll/export/periode/1?export_format=excel" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output paie.xlsx
```

---

### 2. Exporter Toutes les Périodes

```http
GET /api/v1/payroll/export/all-periodes?annee={year}
```

**Paramètres** :
- `annee` (query, optionnel) : Année pour filtrer

**Réponse** : Fichier Excel téléchargeable

**Exemple cURL** :
```bash
curl -X GET "http://localhost:8000/api/v1/payroll/export/all-periodes?annee=2024" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output periodes_2024.xlsx
```

---

### 3. Exporter les Retenues

```http
GET /api/v1/payroll/export/retenues?employe_id={id}
```

**Paramètres** :
- `employe_id` (query, optionnel) : ID de l'employé pour filtrer

**Réponse** : Fichier CSV téléchargeable

**Exemple cURL** :
```bash
curl -X GET "http://localhost:8000/api/v1/payroll/export/retenues?employe_id=123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output retenues.csv
```

---

## 📋 Formats de Fichiers

### Excel (.xlsx)

**Structure pour période** :
- Feuille 1 : Résumé de la période
- Feuille 2 : Détails de paie par employé
- Feuille 3 : Retenues actives

**Avantages** :
- Formatage professionnel
- Plusieurs feuilles
- Formules et calculs
- Idéal pour analyse

### CSV (.csv)

**Structure** :
- Fichier unique avec en-têtes
- Séparateur : virgule
- Encodage : UTF-8 avec BOM

**Avantages** :
- Compatible tous systèmes
- Import facile
- Léger
- Idéal pour traitement automatique

---

## 🔐 Authentification

Tous les endpoints nécessitent :
- Header `Authorization: Bearer {token}`
- Permission `payroll.view`

---

## 📁 Emplacement des Fichiers

Les fichiers sont sauvegardés dans :
```
media/exports/payroll/
```

Format des noms :
- `paie_{annee}_{mois}_{timestamp}.xlsx`
- `paie_{annee}_{mois}_{timestamp}.csv`
- `paie_all_{annee}_{timestamp}.xlsx`
- `retenues_{emp_id}_{timestamp}.csv`

---

## 🎯 Cas d'Usage Rapides

### Archiver la paie du mois
```bash
curl -X GET "http://localhost:8000/api/v1/payroll/export/periode/1" \
  -H "Authorization: Bearer $TOKEN" \
  --output archives/janvier_2024.xlsx
```
id=123" \
  -H "Authorization: Bearer $TOKEN" \
  --output retenues_emp123.csv
```

---

## ⚡ Intégration JavaScript/TypeScript

```typescript
// Fonction utilitaire
async function exportPayroll(
  endpoint: string,
  filename: string,
  token: string
): Promise<void> {
  const response = await fetch(`/api/v1${endpoint}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (!response.ok) throw new Error('Export failed');

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

// Exemples d'utilisation
await exportPayroll(
  '/payroll/export/periode/1?export_format=excel',
  'paie_janvier.xlsx',
  token
);

await exportPayroll(
  '/payroll/export/all-periodes?annee=2024',
  'periodes_2024.xlsx',
  token
);

await exportPayroll(
  '/payroll/export/retenues?employe_id=123',
  'retenues.csv',
  token
);
```

---

## 🐛 Codes d'Erreur

| Code | Message | Solution |
|------|---------|----------|
| 401 | Unauthorized | Vérifier le token |
| 403 | Permission denied | Vérifier les permissions |
| 404 | Not found | Vérifier l'ID |
| 500 | Server error | Contacter l'admin |

---

## 📊 Colonnes Exportées

### Détails Paie (Excel/CSV)
- ID, Employé, Matricule
- Salaire Base, Indemnités (Logement, Déplacement, Fonction)
- Allocation Familiale, Autres Avantages
- Salaire Brut, Cotisations, Base Imposable
- IRE, Retenues Diverses, Salaire Net

### Retenues (CSV)
- ID, Employé ID, Employé
- Type, Description
- Montant Mensuel, Montant Total, Déjà Déduit, Solde
- Date Début, Date Fin, Active, Récurrente

---

## 💡 Conseils

1. **Performance** : Pour >1000 employés, préférer CSV
2. **Archivage** : Utiliser Excel pour conservation
3. **Import** : Utiliser CSV pour systèmes tiers
4. **Nettoyage** : Supprimer régulièrement les anciens exports

---

**Version** : 1.0.0
**Dernière mise à jour** : 2024-02-17
