"""Stock management SQLAlchemy models (workflow-driven).

Toutes les entités métier du module stock vivent ici. Le workflow réutilise
les tables génériques ``cg_statut_processus`` / ``cg_etape_processus`` /
``cg_action_etape_processus`` / ``cg_demande_attribution`` /
``cg_historique_demande`` définies par ``conge_app`` (mêmes tables, FK
directes), exactement comme ``paie_app`` le fait pour ``PeriodePaie``.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class _TimestampMixin:
    """Champs de timestamp réutilisés par toutes les tables stock."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Référentiels
# ---------------------------------------------------------------------------


class CategorieArticle(_TimestampMixin, Base):
    """Catégorie d'articles (Consommable, EPI, Équipement, Bureau, …).

    Éditable en DB → entièrement dynamique.
    """

    __tablename__ = "stk_categorie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    articles: Mapped[list["Article"]] = relationship(
        "Article", back_populates="categorie"
    )


class UniteMesure(_TimestampMixin, Base):
    """Unité de mesure d'un article (pièce, kg, litre, paquet, …).

    Éditable en DB.
    """

    __tablename__ = "stk_unite_mesure"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(50), nullable=False)

    articles: Mapped[list["Article"]] = relationship(
        "Article", back_populates="unite_mesure"
    )


class Article(_TimestampMixin, Base):
    """Article géré en stock."""

    __tablename__ = "stk_article"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nom: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categorie_id: Mapped[int] = mapped_column(
        ForeignKey("stk_categorie.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    unite_mesure_id: Mapped[int] = mapped_column(
        ForeignKey("stk_unite_mesure.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    seuil_alerte: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categorie: Mapped["CategorieArticle"] = relationship(
        "CategorieArticle", back_populates="articles"
    )
    unite_mesure: Mapped["UniteMesure"] = relationship(
        "UniteMesure", back_populates="articles"
    )

    __table_args__ = (
        CheckConstraint("seuil_alerte >= 0", name="ck_article_seuil_positif"),
    )


class StockArticle(_TimestampMixin, Base):
    """Quantité courante d'un article en stock central.

    Une seule ligne par article (1 entrepôt central, choix produit confirmé).
    Mise à jour atomiquement par :class:`MouvementStockService` lors des
    transitions terminales du workflow.
    """

    __tablename__ = "stk_stock_article"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("stk_article.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    quantite: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    article: Mapped["Article"] = relationship("Article")

    __table_args__ = (
        CheckConstraint("quantite >= 0", name="ck_stock_quantite_positive"),
    )


# ---------------------------------------------------------------------------
# Mouvements (ledger immuable)
# ---------------------------------------------------------------------------


class MouvementStock(_TimestampMixin, Base):
    """Ledger des entrées / sorties / ajustements de stock.

    Insertion uniquement (jamais de UPDATE/DELETE en code applicatif) — la
    quantité courante de :class:`StockArticle` est dérivée de la somme.
    """

    __tablename__ = "stk_mouvement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("stk_article.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    type_mouvement: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    quantite: Mapped[float] = mapped_column(Float, nullable=False)
    demande_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("stk_demande.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    auteur_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="SET NULL"), nullable=True, index=True
    )
    employe_attributaire_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="SET NULL"), nullable=True, index=True
    )
    commentaire: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    article: Mapped["Article"] = relationship("Article", foreign_keys=[article_id])

    __table_args__ = (
        CheckConstraint(
            "type_mouvement IN ('ENTREE', 'SORTIE', 'AJUSTEMENT')",
            name="ck_mouvement_type",
        ),
        CheckConstraint("quantite > 0", name="ck_mouvement_quantite_positive"),
        Index("idx_mouvement_article_date", "article_id", "created_at"),
    )


# ---------------------------------------------------------------------------
# Demandes (entité workflow-driven)
# ---------------------------------------------------------------------------


class DemandeStock(_TimestampMixin, Base):
    """Demande de stock (entrée, sortie, ajustement) soumise au workflow.

    Le ``code_processus`` (champ ``processus``) détermine quelles étapes /
    actions s'appliquent — il est borné aux valeurs seedées de
    :class:`CodeProcessusStock` mais peut être étendu à chaud en DB.
    """

    __tablename__ = "stk_demande"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    processus: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    motif: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    demandeur_id: Mapped[int] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    responsable_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="SET NULL"), nullable=True, index=True
    )
    employe_beneficiaire_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="SET NULL"), nullable=True, index=True
    )

    etape_courante_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cg_etape_processus.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    statut_global_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cg_statut_processus.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    date_soumission: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_decision_finale: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    lignes: Mapped[list["DemandeStockLigne"]] = relationship(
        "DemandeStockLigne",
        back_populates="demande",
        cascade="all, delete-orphan",
    )


class DemandeStockLigne(_TimestampMixin, Base):
    """Ligne d'une demande de stock (article + quantité)."""

    __tablename__ = "stk_demande_ligne"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    demande_id: Mapped[int] = mapped_column(
        ForeignKey("stk_demande.id", ondelete="CASCADE"), index=True, nullable=False
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("stk_article.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    quantite: Mapped[float] = mapped_column(Float, nullable=False)

    demande: Mapped["DemandeStock"] = relationship(
        "DemandeStock", back_populates="lignes"
    )
    article: Mapped["Article"] = relationship("Article")

    __table_args__ = (
        CheckConstraint("quantite > 0", name="ck_ligne_quantite_positive"),
        UniqueConstraint("demande_id", "article_id", name="uq_demande_article"),
    )


# ---------------------------------------------------------------------------
# Attribution matériel (qui possède quoi)
# ---------------------------------------------------------------------------


class AttributionMateriel(_TimestampMixin, Base):
    """Trace 'qui possède actuellement quel matériel'.

    Une ligne représente un transfert d'un article vers un employé (matériel
    confié, EPI, badge, …). Quand le matériel est rendu, la ligne est
    archivée (``actif=False``, ``date_retour`` renseignée). Une nouvelle
    ligne est créée à chaque attribution pour conserver l'historique.
    """

    __tablename__ = "stk_attribution_materiel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employe_id: Mapped[int] = mapped_column(
        ForeignKey("rh_employe.id", ondelete="CASCADE"), index=True, nullable=False
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("stk_article.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    quantite: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    demande_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("stk_demande.id", ondelete="SET NULL"), nullable=True, index=True
    )
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    date_attribution: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    date_retour: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    commentaire: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    article: Mapped["Article"] = relationship("Article")

    __table_args__ = (
        CheckConstraint("quantite > 0", name="ck_attribution_quantite_positive"),
        Index("idx_attribution_employe_actif", "employe_id", "actif"),
    )
