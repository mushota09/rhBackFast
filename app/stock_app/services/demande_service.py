"""Service métier pour les demandes de stock (création + soumission workflow)."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.stock_app.constants import CodeProcessusStock
from app.stock_app.models import DemandeStock, DemandeStockLigne
from app.stock_app.services.workflow_service import StockWorkflowService


class DemandeStockService:
    """Crée une demande + lignes + soumet automatiquement au workflow."""

    @staticmethod
    async def creer_et_soumettre(
        db: AsyncSession,
        *,
        processus: str,
        demandeur_id: int,
        responsable_id: Optional[int],
        motif: Optional[str],
        employe_beneficiaire_id: Optional[int],
        lignes: list[dict],
    ) -> DemandeStock:
        """Crée une ``DemandeStock`` + ses lignes, puis lance le workflow.

        ``lignes`` doit être une liste de dicts ``{"article_id": int, "quantite": float}``.

        ``processus`` doit être un code de :class:`CodeProcessusStock`. Les
        codes inconnus sont rejetés par la couche route (Pydantic), mais on
        re-vérifie côté service pour défense en profondeur.
        """
        valid_codes = {p.value for p in CodeProcessusStock}
        if processus not in valid_codes:
            raise ValueError(
                f"Processus '{processus}' inconnu. Codes valides : {valid_codes}"
            )

        demande = DemandeStock(
            processus=processus,
            motif=motif,
            demandeur_id=demandeur_id,
            employe_beneficiaire_id=employe_beneficiaire_id,
        )
        db.add(demande)
        await db.flush()

        for ligne in lignes:
            db.add(
                DemandeStockLigne(
                    demande_id=demande.id,
                    article_id=ligne["article_id"],
                    quantite=ligne["quantite"],
                )
            )
        await db.flush()

        await StockWorkflowService.submit_demande(
            db, demande, responsable_id=responsable_id
        )
        return demande
