# Guide de Gestion des Fichiers - Création Complète d'Employé

## Vue d'ensemble

Le backend rhBackFast a été adapté pour gérer correctement les fichiers lors de la création complète d'un employé via l'endpoint `/api/employees/create-complete`.

## Format du Payload Frontend

Le frontend envoie les données via `FormData` avec les champs suivants :

- `employee` : JSON stringifié contenant les données de l'employé
- `contract` : JSON stringifié contenant les données du contrat
- `documents_metadata` : JSON stringifié contenant un tableau de métadonnées des documents
- `files` : Liste de fichiers (UploadFile) correspondant aux documents
- `password` : (Optionnel) Mot de passe pour le compte utilisateur (défaut: "12345678")
- `group_id` : (Optionnel) ID du groupe à assigner

## Traitement Backend

### 1. Réception des Données

L'endpoint accepte maintenant les paramètres suivants :
```python
async def create_complete_employee(
    employee: str = Form(...),
    contract: str = Form(...),
    documents_metadata: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    password: Optional[str] = Form(default="12345678"),
    group_id: Optional[int] = Form(default=None),
    ...
)
```

### 2. Sauvegarde des Fichiers

Les fichiers sont sauvegardés dans le répertoire `uploads/documents/` avec :
- Génération d'un nom unique via UUID pour éviter les conflits
- Conservation de l'extension originale du fichier
- Création automatique du répertoire si nécessaire

### 3. Stockage en Base de Données

Le chemin relatif du fichier est stocké dans le champ `fichier` du modèle `Document`.

## Structure des Répertoires

```
rhBackFast/
├── uploads/
│   └── documents/
│       ├── {uuid}.pdf
│       ├── {uuid}.jpg
│       └── ...
```

## Sécurité

- Les fichiers sont renommés avec des UUID pour éviter les conflits
- Le répertoire `uploads/` est exclu du contrôle de version (.gitignore)
- Validation des métadonnées avant sauvegarde

- Gestion des erreurs avec rollback en cas d'échec

## Gestion des Erreurs

En cas d'erreur lors de la sauvegarde d'un fichier :
1. Les fichiers déjà sauvegardés sont supprimés
2. La transaction est annulée (rollback)
3. Une erreur HTTP 500 est retournée avec un message explicite

## Exemple de Requête

```javascript
const formData = new FormData();

// Données employé
formData.append('employee', JSON.stringify({
  prenom: 'Jean',
  nom: 'Dupont',
  email_personnel: 'jean.dupont@example.com',
  // ... autres champs
}));

// Données contrat
formData.append('contract', JSON.stringify({
  type_contrat: 'CDI',
  salaire_base: 50000,
  // ... autres champs
}));

// Métadonnées des documents
formData.append('documents_metadata', JSON.stringify([
  {
    type_document: 'CONTRACT',
    titre: 'Contrat de travail',
    description: 'Contrat CDI signé'
  },
  {
    type_document: 'ID',
    titre: 'Carte d\'identité',
    expiry_date: '2030-12-31'
  }
]));

// Fichiers
formData.append('files', contractFile);
formData.append('files', idCardFile);

// Envoi
const response = await axios.post('/api/employees/create-complete', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

## Réponse

```json
{
  "success": true,
  "message": "Employé créé avec succès",
  "data": {
    "employee_id": 123,
    "user_id": 456,
    "contract_id": 789,
    "documents_count": 2,
    "group_assigned": true
  }
}
```

## Configuration Requise

Aucune configuration supplémentaire n'est nécessaire. Le répertoire `uploads/documents/` est créé automatiquement lors de la première utilisation.

## Notes Importantes

1. Les fichiers sans métadonnées correspondantes sont ignorés
2. Les métadonnées sans fichiers sont acceptées (fichier = None)
3. L'ordre des fichiers doit correspondre à l'ordre des métadonnées
4. Taille maximale des fichiers : définie par FastAPI (par défaut illimitée)
