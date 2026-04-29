"""Pydantic schemas for the stock management module."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.stock_app.constants import (
    CodeProcessusStock,
    NomActionStock,
    StatutAttribution,
    TypeMouvement,
)


# ---------------------------------------------------------------------------
# CategorieArticle
# ---------------------------------------------------------------------------


class CategorieBase(BaseModel):
    code: str = Field(..., max_length=30)
    nom: str = Field(..., max_length=100)
    description: Optional[str] = None
    actif: bool = True


class CategorieCreate(CategorieBase):
    pass


class CategorieUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    actif: Optional[bool] = None


class CategorieResponse(CategorieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedCategorie(BaseModel):
    items: list[CategorieResponse]
    total: int
    skip: int
    limit: int


# ---------------------------------------------------------------------------
# UniteMesure
# ---------------------------------------------------------------------------


class UniteMesureBase(BaseModel):
    code: str = Field(..., max_length=20)
    libelle: str = Field(..., max_length=50)


class UniteMesureCreate(UniteMesureBase):
    pass


class UniteMesureUpdate(BaseModel):
    libelle: Optional[str] = Field(None, max_length=50)


class UniteMesureResponse(UniteMesureBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedUniteMesure(BaseModel):
    items: list[UniteMesureResponse]
    total: int
    skip: int
    limit: int


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------


class ArticleBase(BaseModel):
    code: str = Field(..., max_length=50)
    nom: str = Field(..., max_length=150)
    description: Optional[str] = None
    categorie_id: int
    unite_mesure_id: int
    seuil_alerte: float = Field(default=0.0, ge=0)
    actif: bool = True


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    categorie_id: Optional[int] = None
    unite_mesure_id: Optional[int] = None
    seuil_alerte: Optional[float] = Field(None, ge=0)
    actif: Optional[bool] = None


class ArticleResponse(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedArticle(BaseModel):
    items: list[ArticleResponse]
    total: int
    skip: int
    limit: int


# ---------------------------------------------------------------------------
# StockArticle (état courant)
# ---------------------------------------------------------------------------


class StockArticleResponse(BaseModel):
    id: int
    article_id: int
    quantite: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockEtatLigne(BaseModel):
    """Ligne enrichie de l'état du stock (article + qty + alerte)."""

    article_id: int
    article_code: str
    article_nom: str
    categorie: str
    unite: str
    quantite: float
    seuil_alerte: float
    en_alerte: bool


class PaginatedStockEtat(BaseModel):
    items: list[StockEtatLigne]
    total: int
    skip: int
    limit: int


# ---------------------------------------------------------------------------
# Mouvement
# ---------------------------------------------------------------------------


class MouvementResponse(BaseModel):
    id: int
    article_id: int
    type_mouvement: str
    quantite: float
    demande_id: Optional[int]
    auteur_id: Optional[int]
    employe_attributaire_id: Optional[int]
    commentaire: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MouvementManuelRequest(BaseModel):
    """Mouvement manuel hors workflow (ajustement administratif)."""

    article_id: int
    type_mouvement: TypeMouvement
    quantite: float = Field(..., gt=0)
    employe_attributaire_id: Optional[int] = None
    commentaire: Optional[str] = None


class PaginatedMouvement(BaseModel):
    items: list[MouvementResponse]
    total: int
    skip: int
    limit: int


# ---------------------------------------------------------------------------
# Demande de stock
# ---------------------------------------------------------------------------


class DemandeLigneCreate(BaseModel):
    article_id: int
    quantite: float = Field(..., gt=0)


class DemandeLigneResponse(BaseModel):
    id: int
    article_id: int
    quantite: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DemandeStockCreate(BaseModel):
    processus: CodeProcessusStock
    motif: Optional[str] = None
    employe_beneficiaire_id: Optional[int] = None
    lignes: list[DemandeLigneCreate]

    @field_validator("lignes")
    @classmethod
    def _at_least_one_line(cls, value: list[DemandeLigneCreate]) -> list[DemandeLigneCreate]:
        if not value:
            raise ValueError("Au moins une ligne est requise")
        return value


class DemandeStockResponse(BaseModel):
    id: int
    processus: str
    motif: Optional[str]
    demandeur_id: int
    responsable_id: Optional[int]
    employe_beneficiaire_id: Optional[int]
    etape_courante_id: Optional[int]
    statut_global_id: Optional[int]
    date_soumission: Optional[datetime]
    date_decision_finale: Optional[datetime]
    lignes: list[DemandeLigneResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedDemandeStock(BaseModel):
    items: list[DemandeStockResponse]
    total: int
    skip: int
    limit: int


class AppliquerActionRequest(BaseModel):
    action_id: int
    commentaire: Optional[str] = None


# ---------------------------------------------------------------------------
# Workflow runtime config
# ---------------------------------------------------------------------------


class StatutProcessusResponse(BaseModel):
    id: int
    code_statut: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatutProcessusCreate(BaseModel):
    code_statut: str = Field(..., max_length=50)


class EtapeProcessusBase(BaseModel):
    code_processus: str = Field(..., max_length=50)
    ordre: int = Field(..., ge=1)
    nom_etape: str = Field(..., max_length=100)
    poste_id: Optional[int] = None
    is_responsable: bool = False


class EtapeProcessusCreate(EtapeProcessusBase):
    pass


class EtapeProcessusUpdate(BaseModel):
    nom_etape: Optional[str] = Field(None, max_length=100)
    poste_id: Optional[int] = None
    is_responsable: Optional[bool] = None
    ordre: Optional[int] = Field(None, ge=1)


class EtapeProcessusResponse(EtapeProcessusBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionEtapeBase(BaseModel):
    etape_id: int
    nom_action: str = Field(..., max_length=50)
    statut_cible_id: int
    etape_suivante_id: Optional[int] = None


class ActionEtapeCreate(ActionEtapeBase):
    pass


class ActionEtapeUpdate(BaseModel):
    nom_action: Optional[str] = Field(None, max_length=50)
    statut_cible_id: Optional[int] = None
    etape_suivante_id: Optional[int] = None


class ActionEtapeResponse(ActionEtapeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionsPossiblesResponse(BaseModel):
    actions: list[ActionEtapeResponse]
    is_valideur: bool


# ---------------------------------------------------------------------------
# Attribution / historique
# ---------------------------------------------------------------------------


class AttributionResponse(BaseModel):
    id: int
    demande_type: str
    demande_id: int
    etape_id: int
    valideur_attribue_id: int
    statut: str
    date_attribution: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoriqueResponse(BaseModel):
    id: int
    demande_type: str
    demande_id: int
    etape_id: int
    action_id: int
    nouveau_statut_id: int
    valideur_id: Optional[int]
    commentaire: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Attribution matériel
# ---------------------------------------------------------------------------


class AttributionMaterielResponse(BaseModel):
    id: int
    employe_id: int
    article_id: int
    quantite: float
    demande_id: Optional[int]
    actif: bool
    date_attribution: datetime
    date_retour: Optional[datetime]
    commentaire: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttributionMaterielReturn(BaseModel):
    commentaire: Optional[str] = None


class PaginatedAttributionMateriel(BaseModel):
    items: list[AttributionMaterielResponse]
    total: int
    skip: int
    limit: int


# Re-exports for routes
__all__ = [
    "ActionEtapeCreate",
    "ActionEtapeResponse",
    "ActionEtapeUpdate",
    "ActionsPossiblesResponse",
    "AppliquerActionRequest",
    "ArticleCreate",
    "ArticleResponse",
    "ArticleUpdate",
    "AttributionMaterielResponse",
    "AttributionMaterielReturn",
    "AttributionResponse",
    "CategorieCreate",
    "CategorieResponse",
    "CategorieUpdate",
    "DemandeLigneCreate",
    "DemandeLigneResponse",
    "DemandeStockCreate",
    "DemandeStockResponse",
    "EtapeProcessusCreate",
    "EtapeProcessusResponse",
    "EtapeProcessusUpdate",
    "HistoriqueResponse",
    "MouvementManuelRequest",
    "MouvementResponse",
    "NomActionStock",
    "PaginatedArticle",
    "PaginatedAttributionMateriel",
    "PaginatedCategorie",
    "PaginatedDemandeStock",
    "PaginatedMouvement",
    "PaginatedStockEtat",
    "PaginatedUniteMesure",
    "StatutAttribution",
    "StatutProcessusCreate",
    "StatutProcessusResponse",
    "StockArticleResponse",
    "StockEtatLigne",
    "UniteMesureCreate",
    "UniteMesureResponse",
    "UniteMesureUpdate",
]
