# Design Document - Système de Gestion des Congés Professionnelle

## Overview

Ce document décrit l'architecture et la conception détaillée du système de gestion des congés pour rhBackFast. Le système est conçu pour gérer les congés en demi-journées, supporter plusieurs pays avec leurs jours fériés, et fournir une API REST complète avec traçabilité.

### Objectifs Principaux

1. Gérer les congés avec précision (demi-journées)
2. Supporter plusieurs pays et leurs jours fériés
3. Implémenter une validation hiérarchique multi-niveaux
4. Fournir une API REST complète et performante
5. Assurer la traçabilité complète via audit logs
6. Garantir l'intégrité des données

### Technologies Utilisées

- **FastAPI**: Framework web asynchrone
- **SQLAlchemy**: ORM pour la gestion de la base de données
- **Pydantic**: Validation des données et schémas
- **holidays**: Bibliothèque Python pour les jours fériés
- **PostgreSQL**: Base de données relationnelle

## Architecture

### Structure des Modules

```
app/
└── conge_app/
    ├── __init__.py
    ├── models.py          # Modèles SQLAlchemy
    ├── schemas.py         # Schémas Pydantic
    ├── routes.py          # Endpoints FastAPI
    ├── services.py        # Logique métier
    ├── constants.py       # Constantes et énumérations
    └── utils.py           # Utilitaires (calcul jours, etc.)
```

### Dépendances avec les Autres Modules

- **user_app**: Pour les modèles Employe, User, ServiceGroup
- **audit_app**: Pour la traçabilité via AuditService
- **core**: Pour query_utils, security, database

## Components and Interfaces

### 1. Modèles de Données (models.py)

#### TypeConge

```python
class TypeConge(BaseModel):
    """Type de congé (congé payé, maladie, etc.)"""
    __tablename__ = "cg_type_conge"

    nom: Mapped[str]                    # Ex: "Congé Payé"
    code: Mapped[str]                   # Ex: "CP" (unique)
    nb_jours_max_par_an: Mapped[float] # Support demi-journées
    report_autorise: Mapped[bool]       # Peut reporter sur année suivante
    necessite_validation: Mapped[bool]  # Nécessite approbation
    niveaux_validation: Mapped[int]     # Nombre de niveaux requis
    couleur: Mapped[Optional[str]]      # Pour affichage calendrier
    description: Mapped[Optional[str]]

    # Relations
    demandes: Mapped[list["DemandeConge"]]
    soldes: Mapped[list["SoldeConge"]]
```

#### DemandeConge

```python
class DemandeConge(BaseModel):
    """Demande de congé d'un employé"""
    __tablename__ = "cg_demande_conge"

    employe_id: Mapped[int]
    type_conge_id: Mapped[int]
    date_debut: Mapped[date]
    date_fin: Mapped[date]

    # Gestion flexible des congés (jours complets ou demi-journées)
    est_demi_journee: Mapped[bool]      # True si c'est une demi-journée, False si jours complets
    periode_demi_journee: Mapped[Optional[str]]  # "MATIN" ou "APRES_MIDI" (seulement si est_demi_journee=True)
    nb_jours_demandes: Mapped[float]    # Nombre de jours demandés (1.0, 2.0, 5.0, 0.5, etc.)
    nb_jours_ouvrables: Mapped[float]   # Jours ouvrables (excluant weekends et fériés)

    raison: Mapped[str]
    statut: Mapped[str]                 # PENDING, IN_PROGRESS, APPROVED, REJECTED, CANCELLED
    niveau_validation_actuel: Mapped[int] # Niveau en cours (0 = non démarré)

    # Documents justificatifs
    documents: Mapped[list]             # JSON: [{nom, url, type, taille}]

    # Validation
    date_soumission: Mapped[datetime]
    date_decision_finale: Mapped[Optional[datetime]]

    # Relations
    employe: Mapped["Employe"]
    type_conge: Mapped["TypeConge"]
    historique: Mapped[list["HistoriqueConge"]]
```

#### SoldeConge

```python
class SoldeConge(BaseModel):
    """Solde de congés d'un employé pour une année"""
    __tablename__ = "cg_solde_conge"

    employe_id: Mapped[int]
    type_conge_id: Mapped[int]
    annee: Mapped[int]

    # Support demi-journées
    alloue: Mapped[float]               # Jours alloués (ex: 25.5)
    utilise: Mapped[float]              # Jours utilisés (ex: 10.5)
    restant: Mapped[float]              # Calculé: alloue - utilise + reporte
    reporte: Mapped[float]              # Jours reportés année précédente

    date_expiration: Mapped[Optional[date]] # Pour jours reportés

    # Relations
    employe: Mapped["Employe"]
    type_conge: Mapped["TypeConge"]

    # Contrainte unique
    __table_args__ = (
        UniqueConstraint('employe_id', 'type_conge_id', 'annee'),
    )
```

#### HistoriqueConge

```python
class HistoriqueConge(BaseModel):
    """Historique des validations d'une demande"""
    __tablename__ = "cg_historique_conge"

    demande_conge_id: Mapped[int]
    niveau_validation: Mapped[int]      # Niveau de validation (1, 2, 3...)
    valideur_id: Mapped[int]            # User qui a validé
    poste_valideur_id: Mapped[Optional[int]] # ServiceGroup du valideur

    action: Mapped[str]                 # APPROVED, REJECTED, DELEGATED
    date_action: Mapped[datetime]
    commentaire: Mapped[Optional[str]]

    # Délégation
    delegue_a_id:
rved: Mapped[Optional[date]] # Date réellement observée
    annee: Mapped[int]
    est_personnalise: Mapped[bool]      # True si ajouté manuellement

    # Contrainte unique
    __table_args__ = (
        UniqueConstraint('pays_code', 'nom', 'annee'),
    )
```

### 2. Schémas Pydantic (schemas.py)

#### TypeConge Schemas

```python
class TypeCongeBase(BaseModel):
    nom: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    nb_jours_max_par_an: float = Field(default=0, ge=0)
    report_autorise: bool = True
    necessite_validation: bool = True
    niveaux_validation: int = Field(default=1, ge=0, le=5)
    couleur: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None

class TypeCongeCreate(TypeCongeBase):
    pass

class TypeCongeUpdate(BaseModel):
    nom: Optional[str] = None
    nb_jours_max_par_an: Optional[float] = Field(None, ge=0)
    report_autorise: Optional[bool] = None
    necessite_validation: Optional[bool] = None
    niveaux_validation: Optional[int] = Field(None, ge=0, le=5)
    couleur: Optional[str] = None
    description: Optional[str] = None

class TypeCongeResponse(TypeCongeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

#### DemandeConge Schemas

```python
class DemiJourneeEnum(str, Enum):
    MATIN = "MATIN"
    APRES_MIDI = "APRES_MIDI"
    JOURNEE_COMPLETE = "JOURNEE_COMPLETE"

class StatutDemandeEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class DemandeCongeBase(BaseModel):
    employe_id: int
    type_conge_id: int
    date_debut: date
    date_fin: date
    est_demi_journee: bool = False
    periode_demi_journee: Optional[str] = None  # "MATIN" ou "APRES_MIDI"
    raison: str = Field(..., min_length=10)
    documents: List[dict] = []

    @validator('periode_demi_journee')
    def validate_periode(cls, v, values):
        if values.get('est_demi_journee') and not v:
            raise ValueError("periode_demi_journee requis si est_demi_journee=True")
        if not values.get('est_demi_journee') and v:
            raise ValueError("periode_demi_journee doit être None si est_demi_journee=False")
        if v and v not in ["MATIN", "APRES_MIDI"]:
            raise ValueError("periode_demi_journee doit être MATIN ou APRES_MIDI")
        return v

    @validator('date_fin')
    def validate_dates(cls, v, values):
        date_debut = values.get('date_debut')
        est_demi_journee = values.get('est_demi_journee')
        if date_debut and v:
            if est_demi_journee and v != date_debut:
                raise ValueError("Pour une demi-journée, date_debut doit égaler date_fin")
            if not est_demi_journee and v < date_debut:
                raise ValueError("date_fin doit être >= date_debut")
        return v

class DemandeCongeCreate(DemandeCongeBase):
    pass

class DemandeCongeUpdate(BaseModel):
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    debut_demi_journee: Optional[DemiJourneeEnum] = None
    fin_demi_journee: Optional[DemiJourneeEnum] = None
    raison: Optional[str] = None
    documents: Optional[List[dict]] = None

class DemandeCongeResponse(DemandeCongeBase):
    id: int
    nb_jours_demandes: float
    nb_jours_ouvrables: float
    statut: StatutDemandeEnum
    niveau_validation_actuel: int
    date_soumission: datetime
    date_decision_finale: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ApproveRejectRequest(BaseModel):
    commentaire: Optional[str] = None
    delegue_a_id: Optional[int] = None  # Pour délégation
```

#### SoldeConge Schemas

```python
class SoldeCongeBase(BaseModel):
    employe_id: int
    type_conge_id: int
    annee: int = Field(..., ge=2000, le=2100)
    alloue: float = Field(default=0, ge=0)
    reporte: float = Field(default=0, ge=0)
    date_expiration: Optional[date] = None

class SoldeCongeCreate(SoldeCongeBase):
    pass

class SoldeCongeUpdate(BaseModel):
    alloue: Optional[float] = Field(None, ge=0)
    reporte: Optional[float] = Field(None, ge=0)
    date_expiration: Optional[date] = None

class SoldeCongeResponse(SoldeCongeBase):
    id: int
    utilise: float
    restant: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

### 3. Services (services.py)

#### CongeCalculationService

```python
class CongeCalculationService:
    """Service pour les calculs liés aux congés"""

    @staticmethod
    async def calculate_working_days(
        dat
e_debut: date,
        date_fin: date,
        debut_demi: str,
        fin_demi: str,
        pays_code: str,
        db: AsyncSession
    ) -> Tuple[float, float]:
        """
        Calcule le nombre de jours total et ouvrables

        Returns:
            (nb_jours_total, nb_jours_ouvrables)
        """
        # 1. Calculer jours calendaires avec demi-journées
        # 2. Exclure weekends
        # 3. Charger jours fériés du pays
        # 4. Exclure jours fériés
        # 5. Retourner résultats
        pass

    @staticmethod
    async def check_sufficient_balance(
        employe_id: int,
    """
        Vérifie les conflits de dates avec demandes approuvées

        Returns:
            Liste des demandes en conflit
        """
        pass
```

#### HolidayService

```python
class HolidayService:
    """Service pour la gestion des jours fériés"""

    @staticmethod
    async def load_holidays_for_country(
        pays_code: str,
        annee: int,
        db: AsyncSession
    ) -> None:
        """
Charge les jours fériés d'un pays depuis la bibliothèque holidays
        """
        import holidays

        # Charger jours fériés officiels
        country_holidays = holidays.country_holidays(pays_code, years=annee)

        # Sauvegarder en base
        for date_ferie, nom_complet in country_holidays.items():
            # Parser le nom pour extraire le type de date
            nom_propre, type_date = _parse_holiday_name(nom_complet)
            # Vérifier si existe déjà
            # Créer JourFerie avec date_ferie et type_date
            pass

    @staticmethod
    async def get_holidays_between_dates(
        pays_code: str,
        date_debut: date,
        date_fin: date,
        db: AsyncSession
    ) -> List[date]
```python
class ValidationService:
    """Service pour la validation hiérarchique"""

    @staticmethod
    async def get_required_validators(
        demande: DemandeConge,
        db: AsyncSession
    ) -> List[Tuple[int, List[int]]]:
        """
        Détermine les valideurs requis pour chaque niveau

        Returns:
            Liste de (niveau, [user_ids]) pour chaque niveau
        """
        # 1. Récupérer le type de congé et ses niveaux_validation
        # 2. Pour chaque niveau, déterminer les valideurs:
        #    - Niveau 1: Manager direct (responsable_id)
        #    - Niveau 2: Directeur du service
        #    - Niveau 3: RH
        # 3. Retourner la liste ordonnée
        pass

    @staticmethod
    async def can_user_validate(
        user_id: int,
        demande: DemandeConge,
        db: AsyncSession
    ) -> Tuple[bool, int]:
        """
        Vérifie si un utilisateur peut valider une demande

        Returns:
            (can_validate, niveau)
        """
at_level(
        demande_id: int,
        user_id: int,
        commentaire: str,
        db: AsyncSession
    ) -> DemandeConge:
        """
        Rejette une demande

        - Crée un HistoriqueConge
        - Statut = REJECTED
        - Restaure le solde si déjà déduit
        """
        pass

    @staticmethod
    async def delegate_validation(
        demande_id: int,
        from_user_id: int,
        to_user_id: int,
        commentaire: Optional[str],
        db: AsyncSession
    ) -> HistoriqueConge:
        """
        Délègue la validation à un autre utilisateur
        """
        pass
```

#### DemandeCongeService

```python
class DemandeCongeService:
    """Service pour la gestion des demandes de congés"""

    @staticmethod
    async def create_demande(
        demande_data: DemandeCongeCreate,
        db: AsyncSession
    ) -> DemandeConge:
        """
        Crée une nouvelle demande de congé

        Validations:
        1. Employé existe
        2. Type de congé existe
        3. date_debut <= date_fin
        4. Pas de conflit de dates
        5. Solde suffisant
        6. Calcul nb_jours_total et nb_jours_ouvrables
        """
        pass

    @staticmethod
    async def update_demande(
        demande_id: int,
        demande_data: DemandeCongeUpdate,
        db: AsyncSession
    ) -> DemandeConge:
        """
        Met à jour une demande (seulement si PENDING)
        """
        pass

    @staticmethod
    async def cancel_demande(
        demande_id: int,
        user_id: int,
        db: AsyncSession
    ) -> DemandeConge:
        """
        Annule une demande

        - Statut = CANCELLED
        - Restaure le solde si déjà déduit
        """
        pass

    @staticmethod
    async def list_demandes(
        filters: dict,
        expand: Optional[str],
        skip: int,
        limit: int,
        no_pagination: bool,
        db: AsyncSession
    ) -> Tuple[List[DemandeConge], int]:
        """
        Liste les demandes avec filtres et pagination
        """
        pass
```

### 4. Routes API (routes.py)

#### Structure des Routers

```python
# Routers séparés pour chaque ressource
type_conge_router = APIRouter(prefix="/types", tags=["Types de Congé"])
demande_conge_router = APIRouter(prefix="/demandes", tags=["Demandes de Congé"])
solde_conge_router = APIRouter(prefix="/soldes", tags=["Soldes de Congé"])
historique_conge_router = APIRouter(prefix="/historiques", tags=["Historique"])
stats_router = APIRouter(prefix="/stats", tags=["Statistiques"])

# Router principal
router = APIRouter(prefix="/api/conge")
router.include_router(type_conge_router)
router.include_router(demande_conge_router)
router.include_router(solde_conge_router)
router.include_router(historique_conge_router)
router.include_router(stats_router)
```

#### Endpoints Principaux

**TypeConge**:
- `GET /api/conge/types` - Liste des types
- `POST /api/conge/types` - Créer un type
- `GET /api/conge/types/{id}` - Détail d'un type
- `PUT /api/conge/types/{id}` - Modifier un type
- `DELETE /api/conge/types/{id}` - Supprimer un type

**DemandeConge**:
- `GET /api/conge/demandes` - Liste des demandes
- `POST /api/conge/demandes` - Créer une demande
- `GET /api/conge/demandes/{id}` - Détail d'une demande
- `PUT /api/conge/demandes/{id}` - Modifier une demande
- `DELETE /api/conge/demandes/{id}` - Annuler une demande
- `POST /api/conge/demandes/{id}/approve` - Approuver (niveau actuel)
- `POST /api/conge/demandes/{id}/reject` - Rejeter
- `POST /api/conge/demandes/{id}/delegate` - Déléguer validation
- `GET /api/conge/demandes/export` - Exporter les demandes

**SoldeConge**:
- `GET /api/conge/soldes` - Liste des soldes
- `POST /api/conge/soldes` - Créer un solde
- `GET /api/conge/soldes/{id}` - Détail d'un solde
- `PUT /api/conge/soldes/{id}` - Modifier un solde
- `DELETE /api/conge/soldes/{id}` - Supprimer un solde
- `POST /api/conge/soldes/bulk-create` - Créer soldes pour tous employés

**Statistiques**:
- `GET /api/conge/stats` - Statistiques globales
- `GET /api/conge/stats/employe/{id}` - Stats d'un employé
- `GET /api/conge/stats/service/{id}` - Stats d'un service

### 5. Constantes (constants.py)

```python
from enum import Enum

class DemiJournee(str, Enum):
    MATIN = "MATIN"
    APRES_MIDI = "APRES_MIDI"
    JOURNEE_COMPLETE = "JOURNEE_COMPLETE"

class StatutDemande(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class ActionHistorique(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DELEGATED = "DELEGATED"

# Pays supportés (extensible)
PAYS_SUPPORTES = {
    "CD": "République Démocratique du Congo",
    "FR": "France",
    "BE": "Belgique",
    "CA": "Canada",
    # ... autres pays
}

# Permissions
PERMISSIONS = {
    "conge.view": "Consulter les congés",
    "conge.create": "Créer des demandes de congés",
    "conge.update": "Modifier des demandes de congés",
    "conge.delete": "Supprimer des demandes de congés",
    "conge.approve": "Approuver des demandes de congés",
    "conge.manage_types": "Gérer les types de congés",
    "conge.manage_soldes": "Gérer les soldes de congés",
    "conge.export": "Exporter les données de congés",
}
```

### 6. Utilitaires (utils.py)

```python
from datetime import date, timedelta
from typing import List, Tuple

def is_weekend(d: date) -> bool:
    """Vérifie si une date est un weekend"""
    return d.weekday() >= 5  # 5=samedi, 6=dimanche

def count_working_days(
    date_debut: date,
    date_fin: date,
    holidays: List[date]
) -> int:
    """
    Compte les jours ouvrables entre deux dates

    Exclut:
    - Weekends (samedi, dimanche)
    - Jours fériés
    """
    count = 0
    current = date_debut

    while current <= date_fin:
        if not is_weekend(current) and current not in holidays:
            count += 1
        current += timedelta(days=1)

    return count

def calculate_total_days_with_half_days(
    date_debut: date,
    date_fin: date,
    debut_demi: str,
    fin_demi: str
) -> float:
    """
    Calcule le nombre total de jours avec support demi-journées

    Cas 1: Demi-journée isolée (date_debut == date_fin)
    - MATIN ou APRES_MIDI = 0.5 jour
    - JOURNEE_COMPLETE = 1.0 jour

    Cas 2: Plusieurs jours complets (date_debut < date_fin)
    - debut_demi = JOURNEE_COMPLETE et fin_demi = JOURNEE_COMPLETE
    - Calcul: (date_fin - date_debut).days + 1

    Exemples:
    - 1 jour, MATIN, MATIN = 0.5 (demi-journée matin)
    - 1 jour, APRES_MIDI, APRES_MIDI = 0.5 (demi-journée après-midi)
    - 1 jour, JOURNEE_COMPLETE, JOURNEE_COMPLETE = 1.0 (journée complète)
    - 5 jours, JOURNEE_COMPLETE, JOURNEE_COMPLETE = 5.0 (5 jours complets)
    - 9 jours, JOURNEE_COMPLETE, JOURNEE_COMPLETE = 9.0 (9 jours complets)
    """
    if date_debut == date_fin:
        # Demi-journée isolée ou journée complète
        if debut_demi == "JOURNEE_COMPLETE":
            return 1.0
        else:
            # MATIN ou APRES_MIDI = 0.5 jour
            return 0.5

    # Plusieurs jours complets
    # debut_demi et fin_demi doivent être JOURNEE_COMPLETE
    if debut_demi != "JOURNEE_COMPLETE" or fin_demi != "JOURNEE_COMPLETE":
        raise ValueError(
            "Pour des congés de plusieurs jours, "
            "debut_demi_journee et fin_demi_journee doivent être JOURNEE_COMPLETE"
        )

    days = (date_fin - date_debut).days + 1
    return float(days)

def dates_overlap(
    start1: date,
    end1: date,
    start2: date,
    end2: date
) -> bool:
    """Vérifie si deux périodes se chevauchent"""
    return start1 <= end2 and start2 <= end1
```

## Data Models

### Relations entre Modèles

```
Employe (user_app)
    ↓ 1:N
DemandeConge
    ↓ N:1
TypeConge
    ↓ 1:N
SoldeConge
    ↓ N:1
Employe

DemandeConge
    ↓ 1:N
HistoriqueConge
    ↓ N:1
User (valideur)

Employe
    ↓ N:1
Pays (via pays_code)
    ↓ 1:N
JourFerie
```

### Contraintes d'Intégrité

1. **TypeConge.code**: Unique
2. **SoldeConge**: Unique (employe_id, type_conge_id, annee)
3. **JourFerie**: Unique (pays_code, nom, annee)
4. **DemandeConge.date_debut**: <= date_fin
5. **SoldeConge.restant**: >= 0 (soft constraint, alertes si négatif)

### Index de Performance

```sql
-- DemandeConge
CREATE INDEX idx_demande_employe ON cg_demande_conge(employe_id);
CREATE INDEX idx_demande_type ON cg_demande_conge(type_conge_id);
CREATE INDEX idx_demande_statut ON cg_demande_conge(statut);
CREATE INDEX idx_demande_dates ON cg_demande_conge(date_debut, date_fin);

-- SoldeConge
CREATE INDEX idx_solde_employe ON cg_solde_conge(employe_id);
CREATE INDEX idx_solde_annee ON cg_solde_conge(annee);

-- HistoriqueConge
CREATE INDEX idx_historique_demande ON cg_historique_conge(demande_conge_id);
CREATE INDEX idx_historique_valideur ON cg_historique_conge(valideur_id);

-- JourFerie
CREATE INDEX idx_ferie_pays ON cg_jour_ferie(pays_code);
CREATE INDEX idx_ferie_date ON cg_jour_ferie(date_ferie);
```

## Correctness Properties

*Une propriété est une caractéristique ou un comportement qui doit être vrai pour toutes les exécutions valides du système - essentiellement, une déclaration formelle sur ce que le système doit faire. Les propriétés servent de pont entre les spécifications lisibles par l'homme et les garanties de correction vérifiables par machine.*


### Property Reflection

Après analyse des critères d'acceptation, voici les propriétés identifiées avec élimination des redondances:

**Propriétés combinées:**
- Les propriétés 1.1, 1.2, 1.5 peuvent être combinées en une seule propriété sur le calcul des demi-journées
- Les propriétés 4.1-4.5 (CRUD DemandeConge) peuvent être testées via une propriété de round-trip
- Les propriétés 7.1-7.5 (pagination) peuvent être combinées en une propriété générale de pagination
- Les propriétés 8.1-8.6 (expand) peuvent être combinées en une propriété générale d'expansion

**Propriétés redondantes éliminées:**
- 1.3 est un cas particulier de 1.2 (sera géré par les générateurs)
- 2.4 est un edge case géré par la bibliothèque holidays
- 3.1-3.5 sont couverts par une propriété de round-trip CRUD
- 5.1-5.5 sont couverts par une propriété de round-trip CRUD

**Propriétés conservées (valeur unique):**
- Calcul des jours ouvrables avec exclusion des fériés (2.5, 13.1-13.5)
- Validation du solde suffisant (4.8)
- Déduction/restauration du solde (4.9, 4.10)
- Calcul automatique du solde restant (5.6)
- Création automatique d'historique (6.3)
- Détection des conflits de dates (14.1-14.4)
- Validation hiérarchique multi-niveaux (18.1-18.10)

### Correctness Properties

#### Property 1: Half-Day Calculation Consistency
*For any* leave request, if date_debut equals date_fin and debut_demi_journee is MATIN or APRES_MIDI, the calculated total days should be 0.5, and if date_debut is less than date_fin, both debut_demi_journee and fin_demi_journee must be JOURNEE_COMPLETE and the total should equal the number of calendar days.

**Validates: Requirements 1.1, 1.2, 1.5**

#### Property 2: Holiday Data Integrity
*For any* country and year, when holidays are loaded, both estimated and observed dates should be stored separately and retrievable, and custom holidays should be distinguishable from official ones.

**Validates: Requirements 2.3, 2.6, 2.7**

#### Property 3: CRUD Round-Trip for TypeConge
*For any* valid TypeConge object, creating it, reading it back, updating it, and reading again should preserve all field values correctly, and deletion should only succeed if no active leave requests reference it.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

#### Property 4: CRUD Round-Trip for DemandeConge
*For any* valid DemandeConge object, creating it, reading it back, updating it, and reading again should preserve all field values correctly.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

#### Property 5: CRUD Round-Trip for SoldeConge
*For any* valid SoldeConge object, creating it, reading it back, updating it, and reading again should preserve all field values correctly.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

#### Property 6: Working Days Calculation Accuracy
*For any* leave request with start date, end date, half-day specifications, and employee country code, the calculated working days should exclude weekends and the country's holidays (using observed date if available, otherwise estimated).

**Validates: Requirements 2.5, 13.1, 13.2, 13.3, 13.4, 13.5**

#### Property 7: Sufficient Balance Validation
*For any* leave request creation attempt, if the employee's remaining balance for that leave type is less than the requested days, the system should reject the request with an appropriate error message.

**Validates: Requirements 4.8, 11.4**

#### Property 8: Balance Deduction on Approval
*For any* leave request that gets approved at all validation levels, the employee's balance for that leave type should decrease by exactly the number of requested days.

**Validates: Requirements 4.9**

#### Property 9: Balance Restoration on Rejection/Cancellation
*For any* leave request that was approved and then rejected or cancelled, the employee's balance should be restored to its original value before the approval.

**Validates: Requirements 4.10**

#### Property 10: Automatic Balance Calculation
*For any* SoldeConge object, the "restant" field should always equal (alloue - utilise + reporte), and this should be automatically recalculated whenever any of these fields change.

**Validates: Requirements 5.6**

#### Property 11: Automatic History Creation
*For any* leave request that undergoes a status change (approval, rejection, delegation), a corresponding HistoriqueConge entry should be automatically created with the validator, timestamp, action, and comment.

**Validates: Requirements 6.3, 6.4**

#### Property 12: Pagination Consistency
*For any* list endpoint, when called without no_pagination parameter, results should be paginated with default skip=0 and limit=100, and when called with no_pagination=true, all results should be returned with total count matching the number of results.

**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

#### Property 13: Expand Relation Loading
*For any* list or detail endpoint, when the expand parameter is provided with valid relation names (simple, multiple, or nested), the specified relations should be loaded and included in the response without additional queries.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**

#### Property 14: Search and Filter Accuracy
*For any* list endpoint with search or filter parameters, the returned results should match all specified criteria, and multiple filters should be combined with logical AND.

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

#### Property 15: Audit Log Completeness
*For any* create, update, delete, approve, or reject action on leave-related entities, an audit log entry should be created with user, IP, user-agent, timestamp, action type, resource type, resource ID, and old/new values where applicable.

**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7**

#### Property 16: Date Range Validation
*For any* leave request, the start date should be less than or equal to the end date, and if this constraint is violated, the system should return an HTTP 400 error with a descriptive message.

**Validates: Requirements 11.1**

#### Property 17: Entity Existence Validation
*For any* leave request creation, the referenced employee and leave type must exist in the database, otherwise the system should return an HTTP 400 error indicating which entity is missing.

**Validates: Requirements 11.2, 11.3**

#### Property 18: Permission-Based Access Control
*For any* API endpoint, if the current user lacks the required permission (view, create, update, delete, approve), the system should return an HTTP 403 error and not execute the requested action.

**Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6**

#### Property 19: Date Conflict Detection
*For any* leave request creation or approval, if there exists an approved leave request for the same employee with overlapping dates, the system should reject the new request with an HTTP 400 error detailing the conflict.

**Validates: Requirements 14.1, 14.2, 14.3, 14.4**

#### Property 20: Document Attachment Validation
*For any* document attached to a leave request, the file type should be validated (PDF, JPG, PNG only) and size should not exceed 5MB, otherwise the system should return an HTTP 400 error.

**Validates: Requirements 17.3, 17.4**

#### Property 21: Document Cascade Deletion
*For any* leave request that is deleted, all associated document attachments should also be deleted from storage.

**Validates: Requirements 17.5**

#### Property 22: Hierarchical Validation Flow
*For any* leave request requiring multi-level validation, when a validator at level N approves, the request should advance to level N+1 with status IN_PROGRESS, and only when all levels approve should the status become APPROVED and balance be deducted.

**Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.7, 18.8, 18.9**

#### Property 23: Validation Rejection Stops Flow
*For any* leave request in validation, if any validator rejects it, the status should immediately become REJECTED, no further validation levels should be processed, and any deducted balance should be restored.

**Validates: Requirements 18.5**

#### Property 24: Validation Delegation
*For any* validator who delegates their validation to another user, a history entry should be created with action=DELEGATED, and the delegated user should be able to approve/reject at that level.

**Validates: Requirements 18.10**

#### Property 25: Statistics Calculation Accuracy
*For any* statistics query with filters (period, service, leave type), the ca
emande approuvée
5. **Fichiers invalides**: Type ou taille de document non conforme
6. **Données manquantes**: Champs requis non fournis
7. **Format invalide**: Valeurs hors plage ou format incorrect

### Authorization Errors (HTTP 403)

Le système retournera des erreurs HTTP 403 pour:

1. **Permission manquante**: Utilisateur sans permission requise
2. **Validation non autorisée**: Utilisateur pas valideur au niveau actuel
3. **Modification interdite**: Tentative de modifier demande approuvée

### Not Found Errors (HTTP 404)

Le système retournera des erreurs HTTP 404 pour:

1. **Ressource inexistante**: ID non trouvé en base
2. **Endpoint invalide**: Route non définie

### Server Errors (HTTP 500)

Le système retournera des erreurs HTTP 500 pour:

1. **Erreurs de base de données**: Problèmes de connexion ou contraintes
2. **Erreurs inattendues**: Exceptions non gérées

### Error Response Format

```json
{
  "detail": "Message d'erreur descriptif",
  "error_code": "INSUFFICIENT_BALANCE",
  "field": "nb_jours_total",
  "value": 10.5,
  "constraint": "solde_restant >= nb_jours_total"
}
```

## Testing Strategy

### Dual Testing Approach

Le système sera testé avec deux approches complémenta
tion

- **Bibliothèque**: Hypothesis (Python)
- **Itérations mi
nimales**: 100 par test de propriété
- **Stratégies de génération**:
  - Dates valides (2020-2030)
  - Demi-journées (MATIN, APRES_MIDI, JOURNEE_COMPLETE)
  - Soldes positifs et décimaux
  - Pays supportés
  - Statuts valides

### Test Tags

Chaque test de propriété sera tagué avec:

```python
@pytest.mark.property
@pytest.mark.feature("conge-management")
@pytest.mark.validates("Property 1: Half-Day Calculation Consistency")
def test_half_day_calculation_property():
    """
    Feature: conge-management
    P
ongés)
- **Factories**: Génération de données aléatoires valides
- **Mocks**: Services externes (bibliothèque holidays si nécessaire)
- **Database**: Base de test isolée, réinitialisée entre tests

### Performance Testing

- **Load Testing**: 100 requêtes concurrentes
- **Response Time**: < 200ms pour endpoints simples, < 500ms pour calculs complexes
- **Database Queries**: N+1 queries évitées via expand
- **Pagination**: Performance stable avec grands datasets

### Integration Testing

- **API End-to-End**: Tests complets de workflows
- **Validation Flow**: Test du processus multi-niveaux complet
- **Audit Logging**: Vérification de la traçabilité
- **Permission Checks**: Tests d'autorisation

### Test Execution

```bash
# Tous les tests
pytest tests/conge_app/

# Tests de propriétés uniquement
pytest tests/conge_app/ -m property

# Tests avec coverage
pytest tests/conge_app/ --cov=app/conge_app --cov-report=html

# Tests d'une propriété spécifique
pytest tests/conge_app/ -k "half_day_calculation"
```

## Deployment Considerations

### Database Migration

```bash
# Créer la migration
alembic revision --autogenerate -m "Add conge_app tables"

# Appliquer la migration
alembic upgrade head

# Rollback si nécessaire
alembic downgrade -1
```

### Initial Data Setup

1. **Créer les permissions**: Exécuter `create_permissions.py`
2. **Charger les types de congés**: Données initiales (CP, RTT, Maladie, etc.)
3. **Charger les jours fériés**: Pour chaque pays configuré
4. **Créer les soldes**: Pour l'année en cours

### Configuration Environment Variables

```bash
# Pays par défaut
DEFAULT_COUNTRY_CODE=CD

# Jours fériés
HOLIDAYS_AUTO_LOAD=True
HOLIDAYS_YEARS_AHEAD=2

# Validation
MAX_VALIDATION_LEVELS=5
DEFAULT_VALIDATION_LEVELS=2

# Documents
MAX_DOCUMENT_SIZE_MB=5
ALLOWED_DOCUMENT_TYPES=pdf,jpg,jpeg,png

# Audit
AUDIT_ENABLED=True
```

### API Documentation

- **OpenAPI/Swagger**: Disponible sur `/docs`
- **ReDoc**: Disponible sur `/redoc`
- **Exemples**: Inclus dans la documentation API
- **Schémas**: Générés automatiquement par Pydantic

### Monitoring and Logging

- **Application Logs**: Niveau INFO en production
- **Audit Logs**: Tous les changements tracés
- **Performance Metrics**: Temps de réponse, taux d'erreur
- **Alertes**: Soldes négatifs, demandes en attente > 7 jours

### Security Considerations

- **Authentication**: JWT tokens requis
- **Authorization**: Permissions vérifiées sur chaque endpoint
- **Input Validation**: Pydantic schemas + validations custom
- **SQL Injection**: Prévenu par SQLAlchemy ORM
- **XSS**: Prévenu par FastAPI (pas de templates HTML)
- **CSRF**: Non applicable (API REST stateless)
- **Rate Limiting**: À implémenter si nécessaire

### Scalability

- **Database Indexing**: Index sur colonnes fréquemment requêtées
- **Query Optimization**: Utilisation de selectinload pour relations
- **Caching**: Redis pour statistiques (implémentation future)
- **Async Operations**: FastAPI + SQLAlchemy async
- **Pagination**: Obligatoire pour grandes listes

### Backup and Recovery

- **Database Backups**: Quotidiens automatiques
- **Audit Log Retention**: 90 jours minimum
- **Document Storage**: Backup avec les données
- **Disaster Recovery**: Plan de restauration documenté

