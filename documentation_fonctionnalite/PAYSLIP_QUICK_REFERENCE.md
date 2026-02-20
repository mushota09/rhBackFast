# 📄 Génération de Bulletins de Paie - Référence Rapide

## 🚀 Démarrage Rapide

### Générer un bulletin individuel
```bash
curl -X POST "http://localhost:8000/api/v1/paie/payroll/entrees/123/generate-payslip" \
  -H "Authorization: Bearer TOKEN"
```

### Télécharger un bulletin
```bash
curl -X GET "http://localhost:8000/api/v1/paie/payroll/entrees/123/download-payslip" \
  -H "Authorization: Bearer TOKEN" -o bulletin.pdf
```

### Générer tous les bulletins d'une période
```bash
curl -X POST "http://localhost:8000/api/v1/paie/payroll/periodes/10/generate-all-payslips" \
  -H "Authorization: Bearer TOKEN"
```

## 📋 Endpoints

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| POST | `/payroll/entrees/{id}/generate-payslip` | Générer un bulletin | `entree.view` |
| GET | `/payroll/entrees/{id}/download-payslip` | Télécharger un bulletin | `entree.view` |
| POST | `/payroll/periodes/{id}/generate-all-payslips` | Génération en masse | `periode.view` |

## 🔄 Workflow Standard

```
1. POST /periodes                              → Créer période
2. POST /periodes/{id}/process                 → Calculer salaires
3. POST /payroll/periodes/{id}/generate-all    → Générer bulletins
4. POST /periodes/{id}/finalize                → Finaliser
5. POST /periodes/{id}/approve                 → Approuver
6. GET  /payroll/entrees/{id}/download         → Télécharger (optionnel)
```

## 💻 Utilisation Programmatique

### Python
```python
from app.paie_app.services import PayslipGeneratorService

async def generate():
    generator = PayslipGeneratorService(db)
    path = await generator.generate_payslip(entree_id=123)
    print(f"Généré: {path}")
```

### JavaScript
```javascript
const response = await fetch(
  `${baseUrl}/payroll/entrees/123/generate-payslip`,
  { method: 'POST', headers: { Authorization: `Bearer ${token}` } }
);
const result = await response.json();
console.log(result.file_path);
```

## 📁 Structure des Fichiers

```
media/payslips/
└── payslip_{employe_id}_{annee}_{mois}.pdf
```

Exemple: `payslip_123_2024_02.pdf`

## 📄 Contenu du Bulletin

- ✅ En-tête (entreprise, titre, période)
- ✅ Informations employé (nom, matricule, INSS, banque)
- ✅ Détails salaire (base + indemnités = brut)
- ✅ Retenues (INSS, assurance, FPC, IRE)
- ✅ Récapitulatif (brut - retenues = net)
- ✅ Pied de page (date, confidentialité)

## ⚙️ Configuration

### Changer le nom de l'entreprise
Modifier dans `app/paie_app/services/payslip_generator.py`:
```python
def _build_header(self, employe, periode):
    company_name = Paragraph(
        "VOTRE ENTREPRISE",  # ← Modifier ici
        self.styles['CompanyTitle']
    )
```

## 🔍 Vérification

```bash
# Vérifier l'installation
python -c "from app.paie_app.services import PayslipGeneratorService; print('OK')"

# Vérifier ReportLab
python -c "import reportlab; print('OK')"
```

## ❌ Erreurs Courantes

| Erreur | Solution |
|--------|----------|
| `Payroll entry not found` | Vérifier l'ID de l'entrée |
| `Employee not found` | Vérifier que l'employé existe |
| `Period not found` | Vérifier que la période existe |
| `Payslip not generated yet` | Générer d'abord avec POST |
| `Payslip file not found` | Le fichier a été supprimé, régénérer |

## 📊 Modèle de Données

### Champs ajoutés à `EntreePaie`
```python
payslip_generated: bool = False
payslip_file: Optional[str] = None
payslip_generated_at: Optional[datetime] = None
```

## 🔐 Permissions Requises

- **Génération individuelle**: `entree.view`
- **Téléchargement**: `entree.view`
- **Génération en masse**: `periode.view`

## 📚 Documentation Complète

- **PAYSLIP_GENERATION_GUIDE.md** - Guide détaillé
- **PAYSLIP_EXAMPLE.md** - Exemples complets
- **PAYSLIP_IMPLEMENTATION_COMPLETE.md** - Détails techniques

## 🆘 Support

Pour plus d'informations, consultez la documentation complète ou contactez l'équipe de développement.

---

**Version:** 1.0.0 | **Date:** 2024-02-17 | **Statut:** ✅ Production Ready
