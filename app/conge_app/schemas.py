"""Leave management Pydantic schemas"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# TypeConge Schemas
# ============================================================================

class TypeCongeBase(BaseModel):
    """Base schema for TypeConge"""
    nom: str = Field(
        ..., max_length=100, description="Nom du type de congé"
    )
    code: str = Field(
        ..., max_length=20, description="Code unique du type de congé"
    )
    nb_jours_max_par_an: float = Field(
        default=0, ge=0, description="Nombre maximum de jours par an"
    )
    report_autorise: bool = Field(
        default=True, description="Autoriser le report sur l'année suivante"
    )
    necessite_validation: bool = Field(
        default=True, description="Nécessite une validation"
    )
    niveaux_validation: int = Field(
        default=1, ge=0, le=5,
        description="Nombre de niveaux de validation requis"
    )
    couleur: Optional[str] = Field(
        None, max_length=7, description="Couleur pour l'affichage (hex)"
    )
    description: Optional[str] = Field(
        None, description="Description du type de congé"
    )


class TypeCongeCreate(TypeCongeBase):
    """Schema for creating a TypeConge"""
    model_config = ConfigDict(from_attributes=True)


class TypeCongeUpdate(BaseModel):
    """Schema for updating a TypeConge"""
    nom: Optional[str] = Field(None, max_length=100)
    nb_jours_max_par_an: Optional[float] = Field(None, ge=0)
    report_autorise: Optional[bool] = None
    necessite_validation: Optional[bool] = None
    niveaux_validation: Optional[int] = Field(None, ge=0, le=5)
    couleur: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None


class TypeCongeResponse(TypeCongeBase):
    """Schema for TypeConge response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DemandeCongeBase(BaseModel):
    """Base schema for DemandeConge"""
    employe_id: int = Field(..., description="ID de l'employé")
    type_conge_id: int = Field(..., description="ID du type de congé")
    date_debut: date = Field(..., description="Date de début du congé")
    date_fin: date = Field(..., description="Date de fin du congé")
    est_demi_journee: bool = Field(default=False, description="Indique si c'est une demi-journée")
    periode_demi_journee: Optional[str] = Field(None, description="Période de la demi-journée (MATIN ou APRES_MIDI)")
    raison: str = Field(..., min_length=10, description="Raison de la demande de congé")
    documents: List[dict] = Field(default_factory=list, description="Documents justificatifs")

    @field_validator('periode_demi_journee')
    @classmethod
    def validate_periode(cls, v: Optional[str], info) -> Optional[str]:
        """Valide la période de demi-journée"""
        est_demi_journee = info.data.get('est_demi_journee')

        if est_demi_journee and not v:
            raise ValueError("periode_demi_journee requis si est_demi_journee=True")

        if not est_demi_journee and v:
            raise ValueError("periode_demi_journee doit être None si est_demi_journee=False")

        if v and v not in ["MATIN", "APRES_MIDI"]:
            raise ValueError("periode_demi_journee doit être MATIN ou APRES_MIDI")

        return v

    @field_validator('date_fin')
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Valide les dates de début et fin"""
        date_debut = info.data.get('date_debut')
        est_demi_journee = info.data.get('est_demi_journee')

        if date_debut and v:
            if est_demi_journee and v != date_debut:
                raise ValueError("Pour une demi-journée, date_debut doit égaler date_fin")

            if not est_demi_journee and v < date_debut:
                raise ValueError("date_fin doit être >= date_debut")

        return v

class DemandeCongeCreate(DemandeCongeBase):
    """Schema for creating a DemandeConge"""
    pass


class DemandeCongeUpdate(BaseModel):
    """Schema for updating a DemandeConge"""
    date_debut: Optional[date] = Field(None, description="Date de début du congé")
    date_fin: Optional[date] = Field(None, description="Date de fin du congé")
    est_demi_journee: Optional[bool] = Field(None, description="Indique si c'est une demi-journée")
    periode_demi_journee: Optional[str] = Field(None, description="Période de la demi-journée")
    raison: Optional[str] = Field(None, min_length=10, description="Raison de la demande")
    documents: Optional[List[dict]] = Field(None, description="Documents justificatifs")


class DemandeCongeResponse(DemandeCongeBase):
    """Schema for DemandeConge response"""
    id: int
    nb_jours_demandes: float
    nb_jours_ouvrables: float
    statut: str
    niveau_validation_actuel: int
    date_soumission: datetime
    date_decision_finale: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApproveRejectRequest(BaseModel):
    """Schema for approve/reject request"""
    commentaire: Optional[str] = Field(None, description="Commentaire de validation")
    delegue_a_id: Optional[int] = Field(None, description="ID de l'utilisateur à qui déléguer")



# ============================================================================
# SoldeConge Schemas
# ============================================================================

class SoldeCongeBase(BaseModel):
    """Base schema for SoldeConge"""
    employe_id: int = Field(..., description="ID de l'employé")
    type_conge_id: int = Field(..., description="ID du type de congé")
    annee: int = Field(..., ge=2000, le=2100, description="Année du solde")
    alloue: float = Field(default=0, ge=0, description="Jours alloués")
    reporte: float = Field(default=0, ge=0, description="Jours reportés de l'année précédente")
    date_expiration: Optional[date] = Field(None, description="Date d'expiration des jours reportés")


class SoldeCongeCreate(SoldeCongeBase):
    """Schema for creating a SoldeConge"""
    pass


class SoldeCongeUpdate(BaseModel):
    """Schema for updating a SoldeConge"""
    alloue: Optional[float] = Field(None, ge=0)
    reporte: Optional[float] = Field(None, ge=0)
    date_expiration: Optional[date] = None


class SoldeCongeResponse(SoldeCongeBase):
    """Schema for SoldeConge response"""
    id: int
    utilise: float
    restant: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



# ============================================================================
# HistoriqueConge Schemas
# ============================================================================

class HistoriqueCongeResponse(BaseModel):
    """Schema for HistoriqueConge response"""
    id: int
    demande_conge_id: int
    niveau_validation: int
    valideur_id: int
    poste_valideur_id: Optional[int]
    action: str
    date_action: datetime
    commentaire: Optional[str]
    delegue_a_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# JourFerie Schemas
# ============================================================================

class JourFerieBase(BaseModel):
    """Base schema for JourFerie"""
    pays_code: str = Field(
        ...,
        max_length=2,
        description="Code pays ISO 3166-1 alpha-2"
    )
    nom: str = Field(..., max_length=200, description="Nom du jour férié")
    date_ferie: date = Field(..., description="Date du jour férié")
    type_date: str = Field(
        default="NORMAL",
        description="Type de date (NORMAL, ESTIMATED, OBSERVED)"
    )
    annee: int = Field(..., description="Année du jour férié")
    est_personnalise: bool = Field(
        default=False,
        description="Indique si le jour férié est personnalisé"
    )


class JourFerieCreate(JourFerieBase):
    """Schema for creating a JourFerie"""
    pass


class JourFerieResponse(JourFerieBase):
    """Schema for JourFerie response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
