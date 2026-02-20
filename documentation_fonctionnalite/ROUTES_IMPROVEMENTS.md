# Améliorations des Routes rhBackFast

Basé sur l'analyse de rhBack, voici les améliorations à apporter:

## 1. Fonctionnalités Générales à Ajouter

### A. Filtrage et Recherche
- **Filtrage**: Ajouter support pour filtrer par champs (ex: `?poste_id=1&statut_emploi=ACTIVE`)
- **Recherche**: Ajouter recherche textuelle (ex: `?search=Jean`)
- **Tri**: Ajouter tri par colonnes (ex: `?ordering=-created_at`)

### B. Expansion de Champs (FlexFields-like)
- Ajouter paramètre `expand` pour charger relations (ex: `?expand=poste_id,user_account`)
- Optimiser requêtes avec `selectinload` pour relations demandées
- Éviter N+1 queries

### C. Pagination
- Ajouter pagination avec `skip` et `limit`
- Retourner métadonnées (total, page, etc.)

## 2. Améliorations par Module

### EMPLOYE Routes

#### A. GET /employees (List)
**Améliorations:**
```python
- Ajouter filtres: poste_id, poste_id__service_id, statut_emploi
- Ajouter recherche: prenom, nom, postnom, email, matricule
- Ajouter expansion: poste_id, poste_id.service, poste_id.group, user_account
- Optimiser avec selectinload si expand utilisé
- Retourner métadonnées (total_count, active_count)
```

#### B. POST /employees/create-complete
**Nouvelle route** pour création complète (employé + contrat + documents + user):
```python
@employe_router.post("/create-complete")
async def create_complete_employee(
    employee_data: str = Form(...),  # JSON string
    contract_data: str = Form(...),  # JSON string
    documents_metadata: List[str] = Form([]),  # JSON strings
    document_files: List[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer employé co
ment
- Transaction atomique
- Retourner nombre de ServiceGroups créés
```

#### B. DELETE /groups/{id}
**Améliorations:**
```python
- Vérifier si groupe a des utilisateurs actifs
- Empêcher suppression si utilisateurs actifs
- Supprimer ServiceGroups en cascade
- Retourner nombre de ServiceGroups supprimés
```

#### C. GET /groups
**Améliorations:**
```python
- Filtrer par is_active par défaut
- Ajouter expansion: service_groups, user_groups, group_permissions
- Retourner métadonnées (total_groups, active_groups)
```

### SERVICE Routes

#### A. Validation
**Améliorations:**
```python
- Valider unicité du code
- Empêcher suppression si ServiceGroups existent
```

### USER Routes

#### A. GET /users
**Améliorations:**
```python
- Ajouter filtres: employe_id, employe_id__poste_id, is_active
- Ajouter expansion: employe_id, employe_id.poste_id, user_groups
- Optimiser requêtes
```

## 3. Schémas à Ajouter

### A. Schémas de Filtrage
```python
class EmployeFilter(BaseModel):
    poste_id: Optional[int] = None
    statut_emploi: Optional[str] = None
    search: Optional[str] = None
    expand: Optional[str] = None
    skip: int = 0
    limit: int = 100
    or
imal = 0
    devise: str = "USD"

class DocumentMetada
ta(BaseModel):
    document_type: str
    titre: str
    description: Optional[str]
    expiry_date: Optional[date]

class CompleteEmployeeCreate(BaseModel):
    employee: EmployeCreate
    contract: ContratCreate
    documents: List[DocumentMetadata] = []
    password: str = "12345"
```

## 4. Services à Améliorer

### A. EmployeeService
```python
class EmployeeService:
    @staticmethod
    async def create_complete_employee(
        db: AsyncSession,
        employee_data: EmployeCreate,
        contract_data: ContratCreate,
        documents_data: List[tuple[DocumentMetadata, UploadFile]],
        pas
sword: str,
        created_by: User
    ) -> dict:
        """Créer employé complet en transaction atomique"""

    @staticmethod
    async def get_with_relations(
        db: AsyncSession,
        employee_id: int,
        expand: List[str] = []
    ) -> Optional[Employe]:
        """Récupérer employé avec relations optimisées"""

    @staticmethod
    async def list_with_filters(
        db: AsyncSession,
        filters: EmployeFilter
    ) -> tuple[List[Employe], int]:
        """Lister employés avec filtres et pagination"""
```

### B. GroupService
```python
class GroupService:
    @staticmethod
    async def create_with_services(
        db: AsyncSession,
        group_data: GroupCreate,
        service_ids: List[int]
    ) -> tuple[Group, int]:
        """Créer groupe avec ServiceGroups"""

    @staticmethod
    async def delete_with_validation(
        db: AsyncSession,
        group_id: int
    ) -> dict:
        """Supprimer groupe avec validation"""
```

## 5. Utilitaires à Créer

### A. Query Builder
```python
# app/core/query_utils.py

def apply_filters(query, model, filters: dict):
    """Appliquer filtres dynamiques"""

def apply_search(query, model, search_fields: List[str], search_term: str):
    """Appliquer recherche textuelle"""

def apply_ordering(query, model, ordering: str):
    """Appliquer tri"""

def apply_expansion(query, model, expand_fields: List[str]):
    """Appliquer chargement de relations"""
```

## 6. Priorités d'Implémentation

1. **Haute Priorité**:
   - Ajouter `verify_token` et `get_current_user` ✅ (FAIT)
   - Ajouter filtrage de base pour employés
   - Ajouter expansion de champs pour employés
   - Améliorer validation dans GroupService

2. **Moyenne Priorité**:
   - Ajouter endpoint `create-complete` pour employés
   - Ajouter métadonnées dans réponses
   - Améliorer gestion des ServiceGroups

3. **Basse Priorité**:
   - Ajouter recherche textuelle avancée
   - Ajouter tri personnalisé
   - Ajouter cache pour requêtes fréquentes

## 7. Tests à Ajouter

- Tests pour filtrage et recherche
- Tests pour expansion de champs
- Tests pour création complète d'employé
- Tests pour validation de suppression de groupe
- Tests pour gestion des ServiceGroups
