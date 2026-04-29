"""Services métier non-workflow du module stock.

- :class:`MouvementStockService` : insertion atomique d'un mouvement +
  mise à jour idempotente de :class:`StockArticle`.
- :class:`AttributionMaterielService` : suit "qui possède quoi" en
  matérialisant chaque attribution / retour.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.stock_app.constants import TypeMouvement
from app.stock_app.models import (
    Article,
    AttributionMateriel,
    CategorieArticle,
    DemandeStock,
    MouvementStock,
    StockArticle,
    UniteMesure,
)


class StockInsuffisantError(ValueError):
    """Levée quand une sortie demande plus que le stock courant."""


class MouvementStockService:
    """Insère des mouvements et synchronise la quantité courante.

    Toutes les méthodes flushent la session mais ne committent pas — c'est
    la responsabilité de l'appelant (route ou autre service).
    """

    @staticmethod
    async def _ensure_stock_row(db: AsyncSession, article_id: int) -> StockArticle:
        stmt = select(StockArticle).where(StockArticle.article_id == article_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing
        row = StockArticle(article_id=article_id, quantite=0.0)
        db.add(row)
        await db.flush()
        return row

    @classmethod
    async def enregistrer_mouvement(
        cls,
        db: AsyncSession,
        *,
        article_id: int,
        type_mouvement: str,
        quantite: float,
        demande_id: Optional[int] = None,
        auteur_id: Optional[int] = None,
        employe_attributaire_id: Optional[int] = None,
        commentaire: Optional[str] = None,
    ) -> MouvementStock:
        """Insère un mouvement et met à jour la quantité courante de l'article.

        - Type ``ENTREE`` → quantité augmente.
        - Type ``SORTIE`` → quantité diminue (ne peut pas devenir négative).
        - Type ``AJUSTEMENT`` → la ``quantite`` est traitée comme un delta signé,
          mais validée comme positive ici car le sens (positif/négatif) est
          encodé dans des mouvements distincts. Pour un ajustement négatif,
          appeler avec ``type_mouvement=SORTIE`` et ``commentaire=...``.

        Lève :class:`StockInsuffisantError` si une sortie passe en négatif.
        """
        if quantite <= 0:
            raise ValueError("La quantité doit être strictement positive")

        stock = await cls._ensure_stock_row(db, article_id)

        if type_mouvement == TypeMouvement.SORTIE.value:
            if stock.quantite < quantite:
                raise StockInsuffisantError(
                    f"Stock insuffisant pour l'article {article_id} : "
                    f"{stock.quantite} disponible, {quantite} demandé"
                )
            stock.quantite = stock.quantite - quantite
        elif type_mouvement == TypeMouvement.ENTREE.value:
            stock.quantite = stock.quantite + quantite
        elif type_mouvement == TypeMouvement.AJUSTEMENT.value:
            stock.quantite = stock.quantite + quantite
        else:
            raise ValueError(f"Type de mouvement inconnu : {type_mouvement}")

        mouvement = MouvementStock(
            article_id=article_id,
            type_mouvement=type_mouvement,
            quantite=quantite,
            demande_id=demande_id,
            auteur_id=auteur_id,
            employe_attributaire_id=employe_attributaire_id,
            commentaire=commentaire,
        )
        db.add(mouvement)
        await db.flush()
        return mouvement

    @classmethod
    async def appliquer_demande_validee(
        cls,
        db: AsyncSession,
        demande: DemandeStock,
    ) -> list[MouvementStock]:
        """Génère les mouvements correspondant à une demande passée à VALIDE.

        - ``STOCK_SORTIE``  → 1 mouvement ``SORTIE`` par ligne, avec
          ``employe_attributaire_id`` = ``employe_beneficiaire_id``.
        - ``STOCK_ENTREE``  → 1 mouvement ``ENTREE`` par ligne.
        - ``STOCK_AJUSTEMENT`` → 1 mouvement ``AJUSTEMENT`` par ligne.

        Si une attribution matériel est applicable (sortie + bénéficiaire),
        :class:`AttributionMaterielService` la crée également.
        """
        from app.stock_app.constants import CodeProcessusStock

        mouvements: list[MouvementStock] = []

        if demande.processus == CodeProcessusStock.SORTIE.value:
            type_mvt = TypeMouvement.SORTIE.value
        elif demande.processus == CodeProcessusStock.ENTREE.value:
            type_mvt = TypeMouvement.ENTREE.value
        elif demande.processus == CodeProcessusStock.AJUSTEMENT.value:
            type_mvt = TypeMouvement.AJUSTEMENT.value
        else:
            raise ValueError(
                f"Processus stock inconnu : {demande.processus}"
            )

        await db.refresh(demande, attribute_names=["lignes"])

        for ligne in demande.lignes:
            mvt = await cls.enregistrer_mouvement(
                db,
                article_id=ligne.article_id,
                type_mouvement=type_mvt,
                quantite=ligne.quantite,
                demande_id=demande.id,
                auteur_id=demande.demandeur_id,
                employe_attributaire_id=demande.employe_beneficiaire_id,
                commentaire=demande.motif,
            )
            mouvements.append(mvt)

            if (
                demande.processus == CodeProcessusStock.SORTIE.value
                and demande.employe_beneficiaire_id is not None
            ):
                await AttributionMaterielService.creer_attribution(
                    db,
                    employe_id=demande.employe_beneficiaire_id,
                    article_id=ligne.article_id,
                    quantite=ligne.quantite,
                    demande_id=demande.id,
                    commentaire=demande.motif,
                )

        return mouvements


class AttributionMaterielService:
    """Suivi 'qui possède quoi' pour le matériel sorti du stock central."""

    @staticmethod
    async def creer_attribution(
        db: AsyncSession,
        *,
        employe_id: int,
        article_id: int,
        quantite: float,
        demande_id: Optional[int] = None,
        commentaire: Optional[str] = None,
    ) -> AttributionMateriel:
        attribution = AttributionMateriel(
            employe_id=employe_id,
            article_id=article_id,
            quantite=quantite,
            demande_id=demande_id,
            commentaire=commentaire,
            actif=True,
        )
        db.add(attribution)
        await db.flush()
        return attribution

    @staticmethod
    async def lister_par_employe(
        db: AsyncSession,
        employe_id: int,
        *,
        actif_seulement: bool = True,
    ) -> list[AttributionMateriel]:
        stmt = select(AttributionMateriel).where(
            AttributionMateriel.employe_id == employe_id
        )
        if actif_seulement:
            stmt = stmt.where(AttributionMateriel.actif.is_(True))
        result = await db.execute(stmt.order_by(AttributionMateriel.date_attribution.desc()))
        return list(result.scalars().all())

    @classmethod
    async def marquer_retour(
        cls,
        db: AsyncSession,
        attribution_id: int,
        commentaire: Optional[str] = None,
    ) -> AttributionMateriel:
        """Marque une attribution comme rendue + génère un mouvement ``ENTREE``.

        Idempotent : un appel sur une attribution déjà rendue lève une
        ``ValueError``.
        """
        attribution = await db.get(AttributionMateriel, attribution_id)
        if attribution is None:
            raise ValueError(f"Attribution {attribution_id} introuvable")
        if not attribution.actif:
            raise ValueError(
                f"Attribution {attribution_id} déjà rendue le {attribution.date_retour}"
            )
        attribution.actif = False
        attribution.date_retour = datetime.utcnow()
        if commentaire:
            attribution.commentaire = (
                f"{attribution.commentaire or ''}\n[Retour] {commentaire}".strip()
            )
        await MouvementStockService.enregistrer_mouvement(
            db,
            article_id=attribution.article_id,
            type_mouvement=TypeMouvement.ENTREE.value,
            quantite=attribution.quantite,
            commentaire=f"Retour matériel attribution #{attribution.id}",
        )
        await db.flush()
        return attribution


# ---------------------------------------------------------------------------
# Vue agrégée du stock courant (utilisée par les routes /stock/etat)
# ---------------------------------------------------------------------------


async def lister_etat_stock(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    en_alerte_seulement: bool = False,
    categorie_id: Optional[int] = None,
) -> tuple[list[dict], int]:
    """Liste l'état courant agrégé : article + qty + alerte.

    Crée à la volée des lignes ``StockArticle`` à 0 pour les articles qui
    n'en ont pas encore (idempotent, pas de doublon grâce à la contrainte
    UNIQUE sur ``article_id``).
    """
    base_stmt = (
        select(Article, StockArticle, CategorieArticle, UniteMesure)
        .join(CategorieArticle, Article.categorie_id == CategorieArticle.id)
        .join(UniteMesure, Article.unite_mesure_id == UniteMesure.id)
        .outerjoin(StockArticle, StockArticle.article_id == Article.id)
        .where(Article.actif.is_(True))
    )
    if categorie_id is not None:
        base_stmt = base_stmt.where(Article.categorie_id == categorie_id)

    result = await db.execute(base_stmt)
    rows = result.all()

    items: list[dict] = []
    for article, stock, categorie, unite in rows:
        quantite = stock.quantite if stock is not None else 0.0
        en_alerte = quantite <= article.seuil_alerte
        if en_alerte_seulement and not en_alerte:
            continue
        items.append(
            {
                "article_id": article.id,
                "article_code": article.code,
                "article_nom": article.nom,
                "categorie": categorie.nom,
                "unite": unite.code,
                "quantite": quantite,
                "seuil_alerte": article.seuil_alerte,
                "en_alerte": en_alerte,
            }
        )

    total = len(items)
    return items[skip : skip + limit], total
