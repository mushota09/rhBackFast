"""Tests d'intégration pour le workflow dynamique du stock."""
import pytest

from app.conge_app.services.attribution_service import AttributionService
from app.stock_app.constants import (
    CodeStatutStock,
    DemandeTypeStock,
    StatutAttribution,
    TypeMouvement,
)
from app.stock_app.models import (
    AttributionMateriel,
    MouvementStock,
    StockArticle,
)
from app.stock_app.services.stock_service import (
    AttributionMaterielService,
    MouvementStockService,
    StockInsuffisantError,
)
from app.stock_app.services.workflow_service import (
    StockWorkflowPermissionError,
    StockWorkflowService,
    StockWorkflowStateError,
)
from sqlalchemy import select


class TestStockWorkflow:
    @pytest.mark.asyncio
    async def test_submit_positions_demande_at_first_step(
        self, db, stock_workflow_setup
    ):
        setup = stock_workflow_setup
        demande = setup["demande"]

        demande = await StockWorkflowService.submit_demande(
            db, demande, responsable_id=setup["employes"]["responsable"].id
        )
        await db.commit()

        assert demande.etape_courante_id == setup["etapes"]["resp"].id
        assert (
            demande.statut_global_id
            == setup["statuts"][CodeStatutStock.EN_ATTENTE.value].id
        )
        assert demande.responsable_id == setup["employes"]["responsable"].id
        assert demande.date_soumission is not None
        assert demande.date_decision_finale is None

        attributions = await AttributionService.list_attributions_for_step(
            db,
            demande_id=demande.id,
            etape_id=setup["etapes"]["resp"].id,
            demande_type=DemandeTypeStock.DEMANDE_STOCK.value,
        )
        assert len(attributions) == 1
        assert (
            attributions[0].valideur_attribue_id
            == setup["employes"]["responsable"].id
        )
        assert attributions[0].statut == StatutAttribution.PRISE_EN_CHARGE.value

    @pytest.mark.asyncio
    async def test_submit_twice_raises(self, db, stock_workflow_setup):
        setup = stock_workflow_setup
        demande = setup["demande"]
        await StockWorkflowService.submit_demande(
            db, demande, responsable_id=setup["employes"]["responsable"].id
        )
        await db.commit()
        with pytest.raises(StockWorkflowStateError):
            await StockWorkflowService.submit_demande(
                db,
                demande,
                responsable_id=setup["employes"]["responsable"].id,
            )

    @pytest.mark.asyncio
    async def test_non_valideur_cannot_act(self, db, stock_workflow_setup):
        setup = stock_workflow_setup
        demande = setup["demande"]
        await StockWorkflowService.submit_demande(
            db, demande, responsable_id=setup["employes"]["responsable"].id
        )
        await db.commit()

        with pytest.raises(StockWorkflowPermissionError):
            await StockWorkflowService.apply_action(
                db,
                demande=demande,
                action_id=setup["actions"]["resp_appr"].id,
                valideur_employe_id=setup["employes"]["outsider"].id,
            )

    @pytest.mark.asyncio
    async def test_full_workflow_until_validated_creates_movements(
        self, db, stock_workflow_setup
    ):
        setup = stock_workflow_setup
        demande = setup["demande"]
        article = setup["article"]

        # Pré-charger le stock à 20 pour permettre la sortie de 5
        await MouvementStockService.enregistrer_mouvement(
            db,
            article_id=article.id,
            type_mouvement=TypeMouvement.ENTREE.value,
            quantite=20.0,
            commentaire="Stock initial",
        )
        await db.commit()

        # Soumission
        demande = await StockWorkflowService.submit_demande(
            db, demande, responsable_id=setup["employes"]["responsable"].id
        )
        await db.commit()

        # Étape 1 : Responsable approuve → passe à Magasinier
        demande = await StockWorkflowService.apply_action(
            db,
            demande=demande,
            action_id=setup["actions"]["resp_appr"].id,
            valideur_employe_id=setup["employes"]["responsable"].id,
            commentaire="OK responsable",
        )
        await db.commit()
        assert demande.etape_courante_id == setup["etapes"]["mag"].id
        assert (
            demande.statut_global_id
            == setup["statuts"][CodeStatutStock.EN_COURS.value].id
        )
        assert demande.date_decision_finale is None

        # Étape 2 : Magasinier approuve → terminal VALIDE
        demande = await StockWorkflowService.apply_action(
            db,
            demande=demande,
            action_id=setup["actions"]["mag_appr"].id,
            valideur_employe_id=setup["employes"]["magasinier"].id,
            commentaire="Livré",
        )
        await db.commit()

        assert (
            demande.statut_global_id
            == setup["statuts"][CodeStatutStock.VALIDE.value].id
        )
        assert demande.date_decision_finale is not None

        # Mouvements générés : 1 SORTIE pour la ligne de la demande
        result = await db.execute(
            select(MouvementStock).where(MouvementStock.demande_id == demande.id)
        )
        mouvements = list(result.scalars().all())
        assert len(mouvements) == 1
        assert mouvements[0].type_mouvement == TypeMouvement.SORTIE.value
        assert mouvements[0].quantite == 5.0
        assert (
            mouvements[0].employe_attributaire_id
            == setup["employes"]["beneficiaire"].id
        )

        # Stock courant : 20 - 5 = 15
        result = await db.execute(
            select(StockArticle).where(StockArticle.article_id == article.id)
        )
        stock = result.scalar_one()
        assert stock.quantite == 15.0

        # Attribution matériel créée pour SORTIE avec bénéficiaire
        result = await db.execute(
            select(AttributionMateriel).where(
                AttributionMateriel.demande_id == demande.id
            )
        )
        attributions = list(result.scalars().all())
        assert len(attributions) == 1
        assert attributions[0].employe_id == setup["employes"]["beneficiaire"].id
        assert attributions[0].article_id == article.id
        assert attributions[0].quantite == 5.0
        assert attributions[0].actif is True

    @pytest.mark.asyncio
    async def test_reject_at_first_step_stops_workflow(
        self, db, stock_workflow_setup
    ):
        setup = stock_workflow_setup
        demande = setup["demande"]

        await StockWorkflowService.submit_demande(
            db, demande, responsable_id=setup["employes"]["responsable"].id
        )
        await db.commit()

        demande = await StockWorkflowService.apply_action(
            db,
            demande=demande,
            action_id=setup["actions"]["resp_rej"].id,
            valideur_employe_id=setup["employes"]["responsable"].id,
            commentaire="Refusé",
        )
        await db.commit()

        assert (
            demande.statut_global_id
            == setup["statuts"][CodeStatutStock.REJETE.value].id
        )
        assert demande.date_decision_finale is not None
        # Aucun mouvement généré
        result = await db.execute(
            select(MouvementStock).where(MouvementStock.demande_id == demande.id)
        )
        assert result.first() is None


class TestMouvementStockService:
    @pytest.mark.asyncio
    async def test_entree_increase_stock(self, db, stock_workflow_setup):
        article = stock_workflow_setup["article"]

        await MouvementStockService.enregistrer_mouvement(
            db,
            article_id=article.id,
            type_mouvement=TypeMouvement.ENTREE.value,
            quantite=10.0,
        )
        await db.commit()

        result = await db.execute(
            select(StockArticle).where(StockArticle.article_id == article.id)
        )
        stock = result.scalar_one()
        assert stock.quantite == 10.0

    @pytest.mark.asyncio
    async def test_sortie_insufficient_raises(self, db, stock_workflow_setup):
        article = stock_workflow_setup["article"]
        with pytest.raises(StockInsuffisantError):
            await MouvementStockService.enregistrer_mouvement(
                db,
                article_id=article.id,
                type_mouvement=TypeMouvement.SORTIE.value,
                quantite=1.0,
            )

    @pytest.mark.asyncio
    async def test_negative_quantity_rejected(self, db, stock_workflow_setup):
        article = stock_workflow_setup["article"]
        with pytest.raises(ValueError):
            await MouvementStockService.enregistrer_mouvement(
                db,
                article_id=article.id,
                type_mouvement=TypeMouvement.ENTREE.value,
                quantite=-3.0,
            )


class TestAttributionMaterielService:
    @pytest.mark.asyncio
    async def test_marquer_retour_genere_entree(
        self, db, stock_workflow_setup
    ):
        setup = stock_workflow_setup
        article = setup["article"]
        beneficiaire = setup["employes"]["beneficiaire"]

        # Stock initial 20 puis attribution de 5
        await MouvementStockService.enregistrer_mouvement(
            db,
            article_id=article.id,
            type_mouvement=TypeMouvement.ENTREE.value,
            quantite=20.0,
        )
        await db.flush()

        await MouvementStockService.enregistrer_mouvement(
            db,
            article_id=article.id,
            type_mouvement=TypeMouvement.SORTIE.value,
            quantite=5.0,
            employe_attributaire_id=beneficiaire.id,
        )
        attribution = await AttributionMaterielService.creer_attribution(
            db,
            employe_id=beneficiaire.id,
            article_id=article.id,
            quantite=5.0,
        )
        await db.commit()
        assert attribution.actif is True

        # Marquer en retour
        await AttributionMaterielService.marquer_retour(
            db, attribution_id=attribution.id, commentaire="Rendu"
        )
        await db.commit()

        await db.refresh(attribution)
        assert attribution.actif is False
        assert attribution.date_retour is not None

        # Stock = 20 - 5 + 5 = 20
        result = await db.execute(
            select(StockArticle).where(StockArticle.article_id == article.id)
        )
        stock = result.scalar_one()
        assert stock.quantite == 20.0
