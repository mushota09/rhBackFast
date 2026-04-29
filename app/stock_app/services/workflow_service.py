"""Service d'orchestration du workflow pour les demandes de stock.

Réutilise les tables génériques du module ``conge_app``
(``StatutProcessus``, ``EtapeProcessus``, ``ActionEtapeProcessus``,
``DemandeAttribution``, ``HistoriqueDemande``) avec
``demande_type = 'DEMANDE_STOCK'`` et un ``code_processus`` parmi les
valeurs de :class:`CodeProcessusStock` (``STOCK_SORTIE``, ``STOCK_ENTREE``,
``STOCK_AJUSTEMENT``).

Le design est intentionnellement parallèle à
``conge_app.services.workflow_service`` et
``paie_app.services.paie_workflow_service`` pour garantir la cohérence.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conge_app.models import (
    ActionEtapeProcessus,
    EtapeProcessus,
    HistoriqueDemande,
    StatutProcessus,
)
from app.conge_app.services.attribution_service import AttributionService
from app.stock_app.constants import (
    CodeStatutStock,
    DemandeTypeStock,
    StatutAttribution,
)
from app.stock_app.models import DemandeStock


class StockWorkflowConfigError(RuntimeError):
    """Erreur de configuration du workflow stock (étape/statut manquant)."""


class StockWorkflowPermissionError(PermissionError):
    """L'utilisateur n'a pas le droit d'exécuter l'action."""


class StockWorkflowStateError(ValueError):
    """État invalide (étape inconnue, action non applicable, etc.)."""


class StockWorkflowService:
    """Orchestration du workflow stock piloté par la DB."""

    DEMANDE_TYPE = DemandeTypeStock.DEMANDE_STOCK.value

    # ------------------------------------------------------------------
    # Accès aux entités de configuration
    # ------------------------------------------------------------------

    @staticmethod
    async def get_statut_by_code(db: AsyncSession, code_statut: str) -> StatutProcessus:
        stmt = select(StatutProcessus).where(StatutProcessus.code_statut == code_statut)
        statut = (await db.execute(stmt)).scalar_one_or_none()
        if statut is None:
            raise StockWorkflowConfigError(f"Statut '{code_statut}' non configuré")
        return statut

    @staticmethod
    async def get_first_etape(
        db: AsyncSession, code_processus: str
    ) -> EtapeProcessus:
        stmt = (
            select(EtapeProcessus)
            .where(EtapeProcessus.code_processus == code_processus)
            .order_by(EtapeProcessus.ordre.asc())
            .limit(1)
        )
        etape = (await db.execute(stmt)).scalar_one_or_none()
        if etape is None:
            raise StockWorkflowConfigError(
                f"Aucune étape configurée pour le processus '{code_processus}'"
            )
        return etape

    @staticmethod
    async def list_actions_for_etape(
        db: AsyncSession, etape_id: int
    ) -> list[ActionEtapeProcessus]:
        stmt = select(ActionEtapeProcessus).where(
            ActionEtapeProcessus.etape_id == etape_id
        )
        return list((await db.execute(stmt)).scalars().all())

    # ------------------------------------------------------------------
    # Soumission initiale
    # ------------------------------------------------------------------

    @classmethod
    async def submit_demande(
        cls,
        db: AsyncSession,
        demande: DemandeStock,
        responsable_id: Optional[int] = None,
    ) -> DemandeStock:
        """Positionne la demande à l'étape initiale du workflow correspondant.

        - ``etape_courante_id`` ← première étape ordonnée du processus
          ``demande.processus``
        - ``statut_global_id`` ← ``EN_ATTENTE``
        - ``responsable_id`` optionnel (utilisé si une étape ``is_responsable=True``
          est présente dans le workflow)
        - Création des lignes ``DemandeAttribution`` pour la première étape
        """
        if demande.etape_courante_id is not None:
            raise StockWorkflowStateError(
                f"Demande {demande.id} déjà dans le workflow"
            )

        etape = await cls.get_first_etape(db, demande.processus)
        statut_en_attente = await cls.get_statut_by_code(
            db, CodeStatutStock.EN_ATTENTE.value
        )

        demande.etape_courante_id = etape.id
        demande.statut_global_id = statut_en_attente.id
        demande.responsable_id = responsable_id
        demande.date_soumission = datetime.utcnow()
        demande.date_decision_finale = None

        valideurs = await AttributionService.find_valideurs(
            db, etape, responsable_id
        )
        await AttributionService.create_attributions(
            db,
            demande_id=demande.id,
            etape=etape,
            valideurs=valideurs,
            demande_type=cls.DEMANDE_TYPE,
        )
        await db.flush()
        return demande

    # ------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------

    @classmethod
    async def is_user_valideur(
        cls,
        db: AsyncSession,
        demande: DemandeStock,
        employe_id: int,
    ) -> bool:
        """True si l'utilisateur peut agir sur l'étape courante de la demande."""
        if demande.etape_courante_id is None:
            return False
        attribution = await AttributionService.get_attribution_for_user(
            db,
            demande_id=demande.id,
            etape_id=demande.etape_courante_id,
            employe_id=employe_id,
            demande_type=cls.DEMANDE_TYPE,
        )
        if attribution is None:
            return False
        return attribution.statut == StatutAttribution.PRISE_EN_CHARGE.value

    # ------------------------------------------------------------------
    # Application d'une action
    # ------------------------------------------------------------------

    @classmethod
    async def apply_action(
        cls,
        db: AsyncSession,
        demande: DemandeStock,
        action_id: int,
        valideur_employe_id: int,
        commentaire: Optional[str] = None,
    ) -> DemandeStock:
        """Exécute une action sur l'étape courante de la demande.

        - Vérifie que l'utilisateur est bien le valideur attribué.
        - Met à jour ``statut_global`` et ``etape_courante`` selon la config.
        - Enregistre l'historique et marque l'attribution comme ``traitee``.
        - Si fin du workflow → ``date_decision_finale`` + génération des
          mouvements de stock si statut final ``VALIDE``.
        """
        if demande.etape_courante_id is None:
            raise StockWorkflowStateError(
                "Demande non soumise au workflow"
            )

        stmt = select(ActionEtapeProcessus).where(
            ActionEtapeProcessus.id == action_id
        )
        action = (await db.execute(stmt)).scalar_one_or_none()
        if action is None:
            raise StockWorkflowStateError(f"Action {action_id} introuvable")

        if action.etape_id != demande.etape_courante_id:
            raise StockWorkflowStateError(
                "L'action ne s'applique pas à l'étape courante de la demande"
            )

        if not await cls.is_user_valideur(db, demande, valideur_employe_id):
            raise StockWorkflowPermissionError(
                "Vous n'êtes pas le valideur attribué à cette étape"
            )

        etape_actuelle_id = demande.etape_courante_id
        nouveau_statut_id = action.statut_cible_id

        demande.statut_global_id = nouveau_statut_id

        if action.etape_suivante_id is not None:
            demande.etape_courante_id = action.etape_suivante_id
            workflow_termine = False
        else:
            workflow_termine = True

        historique = HistoriqueDemande(
            demande_type=cls.DEMANDE_TYPE,
            demande_id=demande.id,
            etape_id=etape_actuelle_id,
            action_id=action.id,
            nouveau_statut_id=nouveau_statut_id,
            valideur_id=valideur_employe_id,
            commentaire=commentaire,
        )
        db.add(historique)

        await AttributionService.mark_traitee(
            db,
            demande_id=demande.id,
            etape_id=etape_actuelle_id,
            employe_id=valideur_employe_id,
            demande_type=cls.DEMANDE_TYPE,
        )

        if workflow_termine:
            demande.date_decision_finale = datetime.utcnow()
            statut_final = await db.get(StatutProcessus, nouveau_statut_id)
            if (
                statut_final is not None
                and statut_final.code_statut == CodeStatutStock.VALIDE.value
            ):
                # Import local pour éviter le cycle stock_service ↔ workflow.
                from app.stock_app.services.stock_service import (
                    MouvementStockService,
                )

                await MouvementStockService.appliquer_demande_validee(db, demande)
        else:
            etape_suivante = await db.get(EtapeProcessus, demande.etape_courante_id)
            if etape_suivante is None:
                raise StockWorkflowConfigError(
                    f"Étape suivante {demande.etape_courante_id} introuvable"
                )
            valideurs = await AttributionService.find_valideurs(
                db, etape_suivante, demande.responsable_id
            )
            await AttributionService.create_attributions(
                db,
                demande_id=demande.id,
                etape=etape_suivante,
                valideurs=valideurs,
                demande_type=cls.DEMANDE_TYPE,
            )

        await db.flush()
        return demande
