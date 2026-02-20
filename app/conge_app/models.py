"""Leave management models"""
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Date, Text, Float,
    ForeignKey, UniqueConstraint, JSON, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.user_app.models import Employe, User


class BaseModel(Base):
    """Abstract base model with common fields"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class TypeConge(BaseModel):
    """Type de congé (congé payé, maladie, etc.)"""
    __tablename__ = "cg_type_conge"

    nom: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nb_jours_max_par_an: Mapped[float] = mapped_column(
        Float, default=0.0
    )
    report_autorise: Mapped[bool] = mapped_column(Boolean, default=True)
    necessite_validation: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
    niveaux_validation: Mapped[int] = mapped_column(Integer, default=1)
    couleur: Mapped[Optional[str]] = mapped_column(
        String(7), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    demandes: Mapped[list["DemandeConge"]] = relationship(
        "DemandeConge",
        back_populates="type_conge",
        cascade="all, delete-orphan"
    )
    soldes: Mapped[list["SoldeConge"]] = relationship(
        "SoldeConge",
        back_populates="type_conge",
        cascade="all, delete-orphan"
    )


class JourFerie(BaseModel):
    """Jour férié d'un pays"""
    __tablename__ = "cg_jour_ferie"

    pays_code: Mapped[str] = mapped_column(String(2), index=True)
    nom: Mapped[str] = mapped_column(String(200))
    date_ferie: Mapped[date] = mapped_column(Date, index=True)
    type_date: Mapped[str] = mapped_column(
        String(20), default="NORMAL"
    )  # NORMAL, ESTIMATED, OBSERVED
    annee: Mapped[int] = mapped_column(Integer, index=True)
    est_personnalise: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint(
            'pays_code', 'nom', 'annee',
            name='uq_pays_nom_annee'
        ),
        Index('idx_ferie_pays', 'pays_code'),
        Index('idx_ferie_date', 'date_ferie'),
    )


class DemandeConge(BaseModel):
    """Demande de congé d'un employé"""
    __tablename__ = "cg_demande_conge"

    employe_id: Mapped[int] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="CASCADE"),
        index=True
    )
    type_conge_id: Mapped[int] = mapped_column(
        ForeignKey("cg_type_conge.id", ondelete="CASCADE"),
        index=True
    )
    date_debut: Mapped[date] = mapped_column(Date, index=True)
    date_fin: Mapped[date] = mapped_column(Date, index=True)

    # Gestion flexible des congés (jours complets ou demi-journées)
    est_demi_journee: Mapped[bool] = mapped_column(Boolean, default=False)
    periode_demi_journee: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    nb_jours_demandes: Mapped[float] = mapped_column(Float, default=0.0)
    nb_jours_ouvrables: Mapped[float] = mapped_column(Float, default=0.0)

    raison: Mapped[str] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(
        String(20), default="PENDING", index=True
    )
    niveau_validation_actuel: Mapped[int] = mapped_column(
        Integer, default=0
    )

    # Documents justificatifs
    documents: Mapped[list] = mapped_column(JSON, default=list)

    # Validation
    date_soumission: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    date_decision_finale: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Relationships
    type_conge: Mapped["TypeConge"] = relationship(
        "TypeConge", back_populates="demandes"
    )
    historique: Mapped[list["HistoriqueConge"]] = relationship(
        "HistoriqueConge",
        back_populates="demande_conge",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_demande_employe', 'employe_id'),
        Index('idx_demande_type', 'type_conge_id'),
        Index('idx_demande_statut', 'statut'),
        Index('idx_demande_dates', 'date_debut', 'date_fin'),
    )


class SoldeConge(BaseModel):
    """Solde de congés d'un employé pour une année"""
    __tablename__ = "cg_solde_conge"

    employe_id: Mapped[int] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="CASCADE"),
        index=True
    )
    type_conge_id: Mapped[int] = mapped_column(
        ForeignKey("cg_type_conge.id", ondelete="CASCADE")
    )
    annee: Mapped[int] = mapped_column(Integer, index=True)

    # Support demi-journées
    alloue: Mapped[float] = mapped_column(Float, default=0.0)
    utilise: Mapped[float] = mapped_column(Float, default=0.0)
    restant: Mapped[float] = mapped_column(Float, default=0.0)
    reporte: Mapped[float] = mapped_column(Float, default=0.0)

    date_expiration: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True
    )

    # Relationships
    type_conge: Mapped["TypeConge"] = relationship(
        "TypeConge", back_populates="soldes"
    )

    __table_args__ = (
        UniqueConstraint(
            'employe_id', 'type_conge_id', 'annee',
            name='uq_employe_type_annee'
        ),
        Index('idx_solde_employe', 'employe_id'),
        Index('idx_solde_annee', 'annee'),
    )


class HistoriqueConge(BaseModel):
    """Historique des validations d'une demande"""
    __tablename__ = "cg_historique_conge"

    demande_conge_id: Mapped[int] = mapped_column(
        ForeignKey("cg_demande_conge.id", ondelete="CASCADE"),
        index=True
    )
    niveau_validation: Mapped[int] = mapped_column(Integer)
    valideur_id: Mapped[int] = mapped_column(
        ForeignKey("user_management_user.id", ondelete="CASCADE")
    )
    poste_valideur_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rh_service_group.id", ondelete="SET NULL"),
        nullable=True
    )

    action: Mapped[str] = mapped_column(String(20))
    date_action: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    commentaire: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Délégation
    delegue_a_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user_management_user.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    demande_conge: Mapped["DemandeConge"] = relationship(
        "DemandeConge",
        back_populates="historique"
    )

    __table_args__ = (
        Index('idx_historique_demande', 'demande_conge_id'),
        Index('idx_historique_valideur', 'valideur_id'),
    )
