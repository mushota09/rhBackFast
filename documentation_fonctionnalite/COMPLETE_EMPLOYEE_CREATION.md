# Création Complète d'Employé avec Assignation Multi-Groupes

## Vue d'ensemble

L'endpoint `POST /employees/create-complete` permet de créer un employé complet avec toutes ses données associées en une seule transaction atomique.

## Fonctionnalités

### Ce qui est créé en une seule transaction:

1. **Employé** - Toutes les informations personnelles et professionnelles
2. **Contrat** - Contrat de travail avec salaire et indemnités
3. **Documents** - Documents associés (CV, diplômes, etc.)
4. **Compte Utilisateur** - Compte pour se connecter au système
5. **Assignations aux Groupes** - L'utilisateur peut être assigné à plusieurs groupes simultanément

### Avantages

- **Atomicité**: Si une étape échoue, toutes les modifications sont annulées
- **Multi-groupes**: Assignation à plusieurs groupes en une seule opération
- **Validation**: Tous les groupes sont validés avant la création
- **Traçabilité**: Enregistrement de qui a créé l'employé

## Utilisation

### Endpoint

```
POST /employees/create-complete
```

### Authentification

Requiert un token JWT valide (Bearer token)

### Corps de la requête

```json
{
  "employee": {
    "prenom": "Jean",
    "nom": "Dupont",
    "postnom": "Marie",
    "date_naissance": "1990-01-15",
    "sexe": "M",
    "statut_matrimonial": "C",
    "nationalite": "Congolaise",
    "banque": "Equity Bank",
    "numero_compte": "1234567890",
    "niveau_etude": "Licence",
    "numero_inss": "INSS123456",
    "email_personnel": "jean.dupont@email.com",
    "email_professionnel": "jean.dupont@company.com",
    "telephone_personnel": "+243123456789",
    "telephone_professionnel": "+243987654321",
    "adresse_ligne1": "123 Avenue de la Paix",
    "adresse_ligne2": "Appartement 4B",
    "ville": "Kinshasa",
    "province": "Kinshasa",
    "code_postal": "12345",
    "pays": "RDC",
    "matricule": "EMP001",
    "poste_id": 1,
    "responsable_id": 5,
    "date_embauche": "2024-01-01",
    "statut_emploi": "ACTIVE",
    "nombre_enfants": 2,
    "nom_conjoint": "Marie Dupont",
    "biographie": "Expérience de 5 ans en développement",
    "nom_contact_urgence": "Pierre Dupont",
    "lien_contact_urgence": "Frère",
    "telephone_contact_urgence": "+243111222333"
  },
  "contract": {
    "type_contrat": "CDI",
    "date_debut": "2024-01-01",
    "date_fin": null,
    "salaire_base": 1500.00,
    "indemnite_logement": 300.00,
    "indemnite_transport": 200.00,
    "indemnite_fonction": 100.00,
    "devise": "USD"
  },
  "documents_metadata": [
    {
      "type_document": "CV",
      "titre": "CV Jean Dupont",
      "description": "Curriculum Vitae",
      "expiry_date": null
    },
    {
      "type_document": "DIPLOME",
      "titre": "Licence en Informatique",
      "description": "Diplôme universitaire",
      "expiry_date": "2030-12-31"
    }
  ],
  "password": "SecurePassword123!",
  "group_ids": [1, 2, 3]
}
```

### Réponse en cas de succès (200 OK)

```json
{
  "success": true,
  "message": "Employé créé avec succès",
  "data": {
    "employee_id": 42,
    "user_id": 38,
    "contract_id": 15,
    "documents_count": 2,
    "groups_assigned": [
      {
        "group_id": 1,
        "group_code": "DEV",
        "group_name": "Développeurs"
      },
      {
        "group_id": 2,
        "group_code": "ADMIN",
        "group_name": "Administrateurs"
      },
      {
        "group_id": 3,
        "group_code": "MANAGER",
        "group_name": "Managers"
      }
    ]
  }
}
```

### Réponse en cas d'erreur (400 Bad Request)

```json
{
  "detail": "Groupe avec l'ID 5 introuvable ou inactif"
}
```

ou

```json
{
  "detail": "Un compte utilisateur avec l'email jean.dupont@company.com existe déjà"
}
```

## Validation

### Groupes

- Tous les `group_ids` fournis doivent exister
- Tous les groupes doivent être actifs (`is_active = True`)
- Si un groupe est invalide, toute la transaction est annulée

### Email

- L'email professionnel (ou personnel si professionnel absent) doit être unique
- Si l'email existe déjà, la transaction est annulée

### Contrat

- Le salaire de base doit être supérieur à 0
- Les indemnités doivent être >= 0
- La date de début est obligatoire

### Documents

- Le type de document et le titre sont obligatoires
- Les fichiers sont actuellement des placeholders (à implémenter avec upload réel)

## Logique Métier

### Transaction Atomique

Toutes les opérations sont effectuées dans une seule transaction:

```python
# Pseudo-code
BEGIN TRANSACTION
  1. Valider tous les groupes
  2. Créer l'employé
  3. Créer le contrat
  4. Créer les documents
  5. Créer le compte utilisateur
  6. Assigner l'utilisateur aux groupes
COMMIT TRANSACTION

# Si une étape échoue:
ROLLBACK TRANSACTION
```

### Assignation Multi-Groupes

L'utilisateur est assigné à tous les groupes spécifiés:

```python
for group_id in group_ids:
    UserGroup.create(
        user_id=user.id,
        group_id=group_id,
        assigned_by_id=current_user.id,
        is_active=True
    )
```

### Traçabilité

- `created_by`: Enregistre qui a créé l'employé
- `assigned_by_id`: Enregistre qui a assigné l'utilisateur aux groupes
- `uploaded_by`: Enregistre qui a uploadé les documents

## Exemples d'utilisation

### Avec curl

```bash
curl -X POST "http://localhost:8000/api/v1/employees/create-complete" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": {
     "prenom": "Jean",
      "nom": "Dupont",
      ...
    },
    "contract": {
      "type_contrat": "CDI",
      ...
    },
    "documents_metadata": [...],
    "password": "SecurePassword123!",
    "group_ids": [1, 2, 3]
  }'
```

### Avec Python (requests)

```python
import requests

url = "http://localhost:8000/api/v1/employees/create-complete"
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

data = {
    "employee": {
        "prenom": "Jean",
        "nom": "Dupont",
        # ... autres champs
    },
    "contract": {
        "type_contrat": "CDI",
        # ... autres champs
    },
    "documents_metadata": [
        {
            "type_document": "CV",
            "titre": "CV Jean Dupont"
        }
    ],
    "password": "SecurePassword123!",
    "group_ids": [1, 2, 3]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Avec JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/api/v1/employees/create-complete', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    employee: {
      prenom: 'Jean',
      nom: 'Dupont',
      // ... autres champs
    },
    contract: {
      type_contrat: 'CDI',
      // ... autres champs
    },
    documents_metadata: [
      {
        type_document: 'CV',
        titre: 'CV Jean Dupont'
      }
    ],
    password: 'SecurePassword123!',
    group_ids: [1, 2, 3]
  })
});

const result = await response.json();
console.log(result);
```

## Cas d'usage

### Scénario 1: Nouvel employé développeur

Créer un développeur qui doit être dans les groupes "Développeurs" et "Équipe Technique":

```json
{
  "employee": { ... },
  "contract": { ... },
  "documents_metadata": [ ... ],
  "password": "DevPassword123!",
  "group_ids": [1, 5]  // 1=Développeurs, 5=Équipe Technique
}
```

### Scénario 2: Manager multi-départements

Créer un manager qui supervise plusieurs départements:

```json
{
  "employee": { ... },
  "contract": { ... },
  "documents_metadata": [ ... ],
  "password": "ManagerPass123!",
  "group_ids": [3, 7, 9]  // 3=Managers, 7=RH, 9=Finance
}
```

### Scénario 3: Employé simple sans groupes

Créer un employé sans assignation de groupe (peut être fait plus tard):

```json
{
  "employee": { ... },
  "contract": { ... },
  "documents_metadata": [ ... ],
  "password": "EmpPassword123!",
  "group_ids": []  // Aucun groupe
}
```

## Différences avec `/employees/with-user`

| Fonctionnalité | `/with-user` | `/create-complete` |
|----------------|--------------|-------------------|
| Crée l'employé | ✅ | ✅ |
| Crée le compte utilisateur | ✅ | ✅ |
| Crée le contrat | ❌ | ✅ |
| Crée les documents | ❌ | ✅ |
| Assignation groupe | 1 seul | Plusieurs |
| Transaction atomique | Partielle | Complète |

## Notes d'implémentation

### Upload de fichiers

Actuellement, les documents utilisent des placeholders. Pour implémenter l'upload réel:

1. Changer l'endpoint pour accepter `multipart/form-data`
2. Utiliser `File` de FastAPI pour recevoir les fichiers
3. Sauvegarder les fichiers sur le disque ou cloud storage
4. Stocker le chemin dans la base de données

### Performance

Pour de grandes quantités de documents ou de groupes:
- Considérer l'utilisation de `bulk_insert_mappings` pour les insertions
- Limiter le nombre de groupes par employé (ex: max 10)
- Implémenter une file d'attente pour le traitement asynchrone

### Sécurité

- Le mot de passe est hashé avec bcrypt avant stockage
- Seuls les utilisateurs authentifiés peuvent créer des employés
- Les groupes inactifs sont rejetés
- Validation stricte de tous les champs

## Maintenance

### Logs

Tous les échecs sont loggés avec le détail de l'erreur:
- Groupe invalide
- Email en double
- Erreurs de validation

### Monitoring

Métriques à surveiller:
- Temps de réponse de l'endpoint
- Taux d'échec des transactions
- Nombre de groupes assignés par employé

### Tests

Tests à effectuer:
- Création avec to
