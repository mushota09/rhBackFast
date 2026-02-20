# Exemple d'Utilisation - Génération de Bulletins de Paie

## Scénario: Génération des bulletins pour le mois de février 2024

### Étape 1: Créer une période de paie

```bash
curl -X POST "http://localhost:8000/api/v1/paie/periodes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "annee": 2024,
    "mois": 2,
    "date_debut": "2024-02-01",
    "date_fin": "2024-02-29"
  }'
```

**Réponse:**
```json
{
  "id": 10,
  "annee": 2024,
  "mois": 2,
  "statut": "DRAFT",
  ...
}
```

### Étape 2: Traiter la période (calculer les salaires)

```bash
curl -X POST "http://localhost:8000/api/v1/paie/periodes/10/process" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Réponse:**
```json
{
  "processed": 50,
  "errors": 0,
  "warnings": []
}
```

### Étape 3: Générer tous les bulletins de paie

```bash
curl -X POST "http://localhost:8000/api/v1/paie/payroll/periodes/10/generate-all-payslips" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Réponse:**
```json
{
  "message": "Generated 50 payslips successfully",
  "count": 50,
  "file_paths": [
    "media/payslips/payslip_1_2024_02.pdf",
    "media/payslips/payslip_2_2024_02.pdf",
    "media/payslips/payslip_3_2024_02.pdf",
    ...
  ],
  "periode_id": 10
}
```

### Étape 4: Télécharger un bulletin spécifique

```bash
curl -X GET "http://localhost:8000/api/v1/paie/payroll/entrees/123/download-payslip" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o bulletin_jean_dupont.pdf
```

Le fichier PDF sera téléchargé localement.

### Étape 5: Finaliser et approuver la période

```bash
# Finaliser
curl -X POST "http://localhost:8000/api/v1/paie/periodes/10/finalize" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Approuver
curl -X POST "http://localhost:8000/api/v1/paie/periodes/10/approve" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Scénario: Régénérer un bulletin individuel

Si vous devez régénérer un bulletin pour un employé spécifique (par exemple, après une correction):

```bash
# 1. Recalculer l'entrée de paie
curl -X POST "http://localhost:8000/api/v1/paie/entrees/123/calculate" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Régénérer le bulletin
curl -X POST "http://localhost:8000/api/v1/paie/payroll/entrees/123/generate-payslip" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Télécharger le nouveau bulletin
curl -X GET "http://localhost:8000/api/v1/paie/payroll/entrees/123/download-payslip" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o bulletin_corrige.pdf
```

## Exemple avec Python

```python
import httpx
import asyncio

async def generate_payslips_for_period():
    """Exemple complet de génération de bulletins"""

    base_url = "http://localhost:8000/api/v1/paie"
    token = "YOUR_TOKEN"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        # 1. Créer la période
        response = await client.post(
            f"{base_url}/periodes",
            json={
                "annee": 2024,
                "mois": 2,
                "date_debut": "2024-02-01",
                "date_fin": "2024-02-29"
            },
            headers=headers
        )
        periode = response.json()
        periode_id = periode["id"]
        print(f"Période créée: {periode_id}")

        # 2. Traiter la périod
")
        print(f"Fichiers: {result['file_paths'][:3]}...")  # Afficher les 3 premiers

        # 4. Télécharger un bulletin spécifique
        entree_id = 123  # ID de l'entrée
        response = await client.get(
            f"{base_url}/payroll/entrees/{entree_id}/download-payslip",
            headers=headers
        )

        # Sauvegarder le PDF
        with open(f"bulletin_{entree_id}.pdf", "wb") as f:
            f.write(response.content)
        print(f"Bulletin téléchargé: bulletin_{entree_id}.pdf")

        # 5. Finaliser et approuver
        await client.post(
            f"{base_url}/periodes/{periode_id}/finalize",
            headers=headers
        )
        print("Période finalisée")

        await client.post(
            f"{base_url}/periodes/{periode_id}/approve",
            headers=headers
        )
        print("Période approuvée")

# Exécuter
asyncio.run(generate_payslips_for_period())
```

## Exemple avec JavaScript/TypeScript

```typescript
async func
esponse.json();
  const periodeId = periode.id;
  console.log(`Période créée: ${periodeId}`);

  // 2. Traiter la période
  const processResponse = await fetch(
    `${baseUrl}/periodes/${periodeId}/process`,
    { method: "POST", headers }
  );
  const processResult = await processResponse.json();
  console.log(`Traitement: ${processResult.processed} entrées`);

  // 3. Générer tous les bulletins
  const generateResponse = await fetch(
    `${baseUrl}/payroll/periodes/${periodeId}/generate-all-payslips`,
    { method: "POST", headers }
  );
  const generateResult = await generateResponse.json();
  console.log(`Bulletins générés: ${generateResult.count}`);

  // 4. Télécharger un bulletin spécifique
  const entreeId = 123;
  const downloadResponse = await fetch(
    `${baseUrl}/payroll/entrees/${entreeId}/download-payslip`,
    { headers }
  );
  const blob = await downloadResponse.blob();

  // Créer un lien de téléchargement
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `bulletin_${entreeId}.pdf`;
  a.click();

  console.log("Bulletin téléchargé");
}
```

## Structure du PDF Généré

Le bulletin de paie généré contient:

```
┌─────────────────────────────────────────┐
│         VOTRE ENTREPRISE                │
│                                         │
│       BULLETIN DE PAIE                  │
│        Février 2024                     │
├─────────────────────────────────────────┤
│  INFORMATIONS EMPLOYÉ                   │
│  Nom complet:    Jean DUPONT            │
│  Matricule:      EMP001                 │
│  Numéro INSS:    123456789              │
│  Banque:         Banque XYZ             │
│  Compte:         1234567890             │
├─────────────────────────────────────────┤
│  DÉTAILS DU SALAIRE                     │
│  Salaire de base         1,000.00 USD   │
│  Indemnité de logement     200.00 USD   │
│  Indemnité de fonction     150.00 USD   │
│  ─────────────────────────────────────  │
│  SALAIRE BRUT            1,350.00 USD   │
├─────────────────────────────────────────┤
│  RETENUES ET COTISATIONS                │
│  INSS Employé               67.50 USD   │
│  Assurance Employé          13.50 USD   │
│  IRE                        45.00 USD   │
│  ─────────────────────────────────────  │
│  TOTAL RETENUES            126.00 USD   │
├─────────────────────────────────────────┤
│  RÉCAPITULATIF                          │
│  Salaire Brut            1,350.00 USD   │
│  Total Retenues            126.00 USD   │
│  ─────────────────────────────────────  │
│  SALAIRE NET À PAYER     1,224.00 USD   │
├─────────────────────────────────────────┤
│  Document généré le 17/02/2024 à 14:30  │
│  Ce bulletin est confidentiel...        │
└─────────────────────────────────────────┘
```

## Notes Importantes

1. **Permissions**: Assurez-vous d'avoir les permissions appropriées:
   - `entree.view` pour générer/télécharger des bulletins individuels
   - `periode.view` pour générer en masse

2. **Ordre des opérations**: Respectez l'ordre:
   - Créer → Traiter → Générer bulletins → Finaliser → Approuver

3. **Stockage**: Les bulletins sont sauvegardés dans `media/payslips/`

4. **Régénération**: Vous pouvez régénérer un bulletin à tout moment, l'ancien sera écrasé

5. **Audit**: Toutes les opérations sont auditées automatiquement
