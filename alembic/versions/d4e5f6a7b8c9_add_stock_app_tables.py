"""Add stock_app tables.

Crée les 8 tables du module ``stock_app`` :

- ``stk_categorie`` (référentiel catégorie d'articles)
- ``stk_unite_mesure`` (référentiel unité de mesure)
- ``stk_article`` (article géré en stock)
- ``stk_stock_article`` (quantité courante par article — 1 ligne / article)
- ``stk_mouvement`` (ledger entrée/sortie/ajustement)
- ``stk_demande`` (demande workflow-driven : sortie / entrée / ajustement)
- ``stk_demande_ligne`` (ligne d'une demande)
- ``stk_attribution_materiel`` (qui possède quoi)

Le workflow lui-même réutilise les tables ``cg_*`` (statuts / étapes /
actions / attributions / historique) définies par ``conge_app``.

Revision ID: d4e5f6a7b8c9
Revises: f5a6b7c8d9e0
Create Date: 2026-04-20 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "f5a6b7c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stk_categorie",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_stk_categorie_code", "stk_categorie", ["code"])

    op.create_table(
        "stk_unite_mesure",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("libelle", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_stk_unite_mesure_code", "stk_unite_mesure", ["code"])

    op.create_table(
        "stk_article",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("nom", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("categorie_id", sa.Integer(), nullable=False),
        sa.Column("unite_mesure_id", sa.Integer(), nullable=False),
        sa.Column(
            "seuil_alerte", sa.Float(), nullable=False, server_default="0"
        ),
        sa.Column(
            "actif", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["categorie_id"], ["stk_categorie.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["unite_mesure_id"], ["stk_unite_mesure.id"], ondelete="RESTRICT"
        ),
        sa.CheckConstraint(
            "seuil_alerte >= 0", name="ck_article_seuil_positif"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_stk_article_code", "stk_article", ["code"])
    op.create_index(
        "ix_stk_article_categorie_id", "stk_article", ["categorie_id"]
    )
    op.create_index(
        "ix_stk_article_unite_mesure_id", "stk_article", ["unite_mesure_id"]
    )

    op.create_table(
        "stk_stock_article",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("quantite", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["article_id"], ["stk_article.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "quantite >= 0", name="ck_stock_quantite_positive"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("article_id"),
    )
    op.create_index(
        "ix_stk_stock_article_article_id",
        "stk_stock_article",
        ["article_id"],
    )

    op.create_table(
        "stk_demande",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("processus", sa.String(length=50), nullable=False),
        sa.Column("motif", sa.Text(), nullable=True),
        sa.Column("demandeur_id", sa.Integer(), nullable=False),
        sa.Column("responsable_id", sa.Integer(), nullable=True),
        sa.Column("employe_beneficiaire_id", sa.Integer(), nullable=True),
        sa.Column("etape_courante_id", sa.Integer(), nullable=True),
        sa.Column("statut_global_id", sa.Integer(), nullable=True),
        sa.Column("date_soumission", sa.DateTime(), nullable=True),
        sa.Column("date_decision_finale", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["demandeur_id"], ["rh_employe.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["responsable_id"], ["rh_employe.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["employe_beneficiaire_id"],
            ["rh_employe.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["etape_courante_id"],
            ["cg_etape_processus.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["statut_global_id"],
            ["cg_statut_processus.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stk_demande_processus", "stk_demande", ["processus"])
    op.create_index(
        "ix_stk_demande_demandeur_id", "stk_demande", ["demandeur_id"]
    )
    op.create_index(
        "ix_stk_demande_responsable_id", "stk_demande", ["responsable_id"]
    )
    op.create_index(
        "ix_stk_demande_beneficiaire_id",
        "stk_demande",
        ["employe_beneficiaire_id"],
    )
    op.create_index(
        "ix_stk_demande_etape_id", "stk_demande", ["etape_courante_id"]
    )
    op.create_index(
        "ix_stk_demande_statut_id", "stk_demande", ["statut_global_id"]
    )

    op.create_table(
        "stk_demande_ligne",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("demande_id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("quantite", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["demande_id"], ["stk_demande.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["article_id"], ["stk_article.id"], ondelete="RESTRICT"
        ),
        sa.CheckConstraint("quantite > 0", name="ck_ligne_quantite_positive"),
        sa.UniqueConstraint(
            "demande_id", "article_id", name="uq_demande_article"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stk_demande_ligne_demande_id",
        "stk_demande_ligne",
        ["demande_id"],
    )
    op.create_index(
        "ix_stk_demande_ligne_article_id",
        "stk_demande_ligne",
        ["article_id"],
    )

    op.create_table(
        "stk_mouvement",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("type_mouvement", sa.String(length=20), nullable=False),
        sa.Column("quantite", sa.Float(), nullable=False),
        sa.Column("demande_id", sa.Integer(), nullable=True),
        sa.Column("auteur_id", sa.Integer(), nullable=True),
        sa.Column("employe_attributaire_id", sa.Integer(), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["article_id"], ["stk_article.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["demande_id"], ["stk_demande.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["auteur_id"], ["rh_employe.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["employe_attributaire_id"],
            ["rh_employe.id"],
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "type_mouvement IN ('ENTREE', 'SORTIE', 'AJUSTEMENT')",
            name="ck_mouvement_type",
        ),
        sa.CheckConstraint(
            "quantite > 0", name="ck_mouvement_quantite_positive"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stk_mouvement_article_id", "stk_mouvement", ["article_id"]
    )
    op.create_index(
        "ix_stk_mouvement_type", "stk_mouvement", ["type_mouvement"]
    )
    op.create_index(
        "ix_stk_mouvement_demande_id", "stk_mouvement", ["demande_id"]
    )
    op.create_index(
        "ix_stk_mouvement_auteur_id", "stk_mouvement", ["auteur_id"]
    )
    op.create_index(
        "ix_stk_mouvement_attributaire_id",
        "stk_mouvement",
        ["employe_attributaire_id"],
    )
    op.create_index(
        "idx_mouvement_article_date",
        "stk_mouvement",
        ["article_id", "created_at"],
    )

    op.create_table(
        "stk_attribution_materiel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employe_id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("quantite", sa.Float(), nullable=False),
        sa.Column("demande_id", sa.Integer(), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "date_attribution",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_retour", sa.DateTime(), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["employe_id"], ["rh_employe.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["article_id"], ["stk_article.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["demande_id"], ["stk_demande.id"], ondelete="SET NULL"
        ),
        sa.CheckConstraint(
            "quantite > 0", name="ck_attribution_quantite_positive"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stk_attribution_employe_id",
        "stk_attribution_materiel",
        ["employe_id"],
    )
    op.create_index(
        "ix_stk_attribution_article_id",
        "stk_attribution_materiel",
        ["article_id"],
    )
    op.create_index(
        "ix_stk_attribution_demande_id",
        "stk_attribution_materiel",
        ["demande_id"],
    )
    op.create_index(
        "idx_attribution_employe_actif",
        "stk_attribution_materiel",
        ["employe_id", "actif"],
    )
    op.create_index(
        "ix_stk_attribution_actif",
        "stk_attribution_materiel",
        ["actif"],
    )


def downgrade() -> None:
    op.drop_table("stk_attribution_materiel")
    op.drop_table("stk_mouvement")
    op.drop_table("stk_demande_ligne")
    op.drop_table("stk_demande")
    op.drop_table("stk_stock_article")
    op.drop_table("stk_article")
    op.drop_table("stk_unite_mesure")
    op.drop_table("stk_categorie")
