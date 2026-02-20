# Guide de Génération des Bulletins de Paie (PDF)

## Vue d'ensemble

Le module de génération de bulletins de paie permet de créer automatiquement des bulletins de paie au format PDF pour les employés. Cette fonctionnalité utilise la bibliothèque ReportLab pour générer des documents PDF professionnels et bien formatés.

## Fonctionnalités

### 1. Génération de bulletin individuel
- Génère un bulletin de paie PDF pour une entrée de paie spécifique
- Inclut toutes les informations de l'employé et les détails du salaire
- Sauvegarde automatique dans le dossier `media/payslips/`
- Mise à jour automatique de l'enregistrement de l'entrée de paie

### 2. Génération en masse
- Génère des bulletins de paie pour tous les employés d'une période
- Traitement automatique de toutes les entrées de paie
- Gestion des erreurs pour continuer même si une génération échoue

### 3. Téléchargement de bulletin
- Télécharge un bulletin de paie déjà généré
- Vérification de l'existence du fichier
- Retour du PDF avec le bon type MIME

## Structure du Bulletin de Paie

Chaque bulletin de paie contient les sections suivantes :

### En-tête
- Nom de l'entreprise
- Titre "BULLETIN DE PAIE"
- Mois et année de la période

### Informations Employé
- Nom complet
- Matricule
- Numéro INSS
- Banque
- Numéro de compte

### Détails du Salaire
- Salaire de base
- Indemnité de logement (si applicable)
- Indemnité de déplacement (si applicable)
- Indemnité de fonction (si applicable)
- Allocation familiale (si applicable)
- Autres avantages (si applicable)
- **SALAIRE BRUT** (total)

### Retenues et Cotisations
- INSS Employé
- Assurance Employé
- FPC Employé
- IRE (Impôt sur le Revenu)
- Retenues diverses
- **TOTAL RETENUES**

### Récapitulatif
- Salaire Brut
- Total Retenues
- **SALAIRE NET À PAYER** (mis en évidence)

### Pied de page
- Date et heure de génération
- Mention de confidentialité

## API Endpoints

### 1. Générer un bulletin individuel

```http
POST /payroll/entrees/{entree_id}/generate-payslip
```

**Paramètres:**
- `entree_id` (path): ID de l'entrée de paie

**Permissions requises:** `entree.view`

**Réponse:**
```json
{
  "message": "Payslip generated successfully",
  "file_path": "media/payslips/payslip_123_2024_02.pdf",
  "entree_id": 123
}
```

**Exemple d'utilisation:**
```bash
curl -X POST "http://localhost:8000/api/v1/paie/payroll/entrees/123/generate-payslip" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Télécharger un bulletin

```http
GET /payroll/entrees/{entree_id}/download-payslip
```

**Paramètres:**
- `entree_id` (path): ID de l'entrée de paie

**Permissions requises:** `entree.view`

**Réponse:** Fichier PDF

**Exemple d'utilisation:**
```bash
curl -X GET "http://localhost:8000/api/v1/paie/payroll/entrees/123/download-payslip" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o bulletin_paie.pdf
```

### 3. Générer tous les bulletins d'une période

```http
POST /payroll/periodes/{periode_id}/generate-all-payslips
```

**Paramètres:**
- `periode_id` (path): ID de la période de paie

**Permissions requises:** `periode.view`

**Réponse:**
```json
{
  "message": "Generated 50 payslips successfully",
  "count": 50,
  "file_paths": [
    "media/payslips/payslip_1_2024_02.pdf",
    "media/payslips/payslip_2_2024_02.pdf",
    ...
  ],
  "periode_id": 10
}
```

**Exemple d'utilisation:**
```bash
curl -X POST "http://localhost:8000/api/v1/paie/payroll/periodes/10/generate-all-payslips" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Utilisation Programmatique

### Exemple avec le Service

```python
from app.paie_app.services import PayslipGeneratorService
from app.core.database import get_db

async def generate_payslip_example():
    async with get_db() as db:
        generator = PayslipGeneratorService(db)

        # Générer un bulletin individuel
        file_path = await generator.generate_payslip(
            entree_id=123
        )
        print(f"Bulletin généré: {file_path}")

        # Générer tous les bulletins d'une période
        file_paths = await gen
ns `PayslipGeneratorService`:

```python
def _build_header(self, employe: Employe, periode: PeriodePaie) -> list:
    # ...
    company_name = Paragraph(
        "VOTRE ENTREPRISE",  # Changez ici
        self.styles['CompanyTitle']
    )
    # ...
```

## Gestion des Erreurs

### Erreurs courantes

1. **Entrée de paie non trouvée**
   ```json
   {
     "detail": "Payroll entry 123 not found"
   }
   ```

2. **Employé non trouvé**
   ```json
   {
     "detail": "Employee 456 not found"
   }
   ```

3. **Période non trouvée**
   ```json
   {
     "detail": "Period 10 not found"
   }
   ```

4. **Bulletin non généré**
   ```json
   {
     "detail": "Payslip not generated yet. Please generate it first."
   }
   ```

5. **Fichier non trouvé**
   ```json
   {
     "detail": "Payslip file not found on disk"
   }
   ```

## Audit

Toutes les opérations de génération de bulletins sont auditées :

- **Génération individuelle**: Action `CREATE` sur ressource `payslip`
- **Génération en masse**: Action `CREATE` sur ressource `payslip_bulk`
- Inclut le chemin du fichier et le nombre de bulletins générés

## Modèle de Données

### Champs ajoutés à `EntreePaie`

```python
payslip_generated: bool = False
payslip_file: Optional[str] = None
payslip_generated_at: Optional[datetime] = None
```

Ces champs sont automatiquement mis à jour lors de la génération d'un bulletin.

## Dépendances

### Bibliothèque ReportLab

```toml
dependencies = [
    # ...
    "reportlab>=4.0.0",
]
```

Installation:
```bash
uv add reportlab
# ou
pip install reportlab
```

## Tests

### Test d'importation

```bash
python -c "from app.paie_app.services import PayslipGeneratorService; print('OK')"
```

### Test des routes

```bash
python -c "from app.paie_app.routes import get_paie_app_router; print('OK')"
```

## Workflow Recommandé

1. **Traiter la période de paie**
   ```
   POST /periodes/{periode_id}/process
   ```

2. **Finaliser la période**
   ```
   POST /periodes/{periode_id}/finalize
   ```

3. **Générer tous les bulletins**
   ```
   POST /payroll/periodes/{periode_id}/generate-all-payslips
   ```

4. **Approuver la période**
   ```
   POST /periodes/{periode_id}/approve
   ```

5. **Télécharger les bulletins individuels** (si nécessaire)
   ```
   GET /payroll/entrees/{entree_id}/download-payslip
   ```

## Améliorations Futures

- [ ] Support de plusieurs langues (FR, EN)
- [ ] Personnalisation du logo de l'entreprise
- [ ] Export en ZIP pour génération en masse
- [ ] Envoi automatique par email
- [ ] Signature numérique
- [ ] Watermark pour les brouillons
- [ ] Templates personnalisables
- [ ] Support de plusieurs devises

## Support

Pour toute question ou problème, consultez la documentation technique ou contactez l'équipe de développement.

---

**Date de création:** 2024-02-17
**Version:** 1.0.0
**Statut:** ✅ Implémenté et testé
