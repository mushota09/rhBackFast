"""Tests for ValidationService.approve_at_level"""
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.conge_app.models import (
    TypeConge,
    DemandeConge,
    SoldeConge,
    HistoriqueConge
)
from app.conge_app.services import ValidationService
tionHistorique


@pytest.mark.asyncio
async def test_approve_at_level_single_level(db_session: AsyncSession):
    """Test approval when there's only one validation level"""
    # Create a type de congé with 1 validation level
    type_conge = TypeCong
        nom="Congé Payé",
        code="CP",
        nb_jours_max_par_an=25.0,
        report_autorise=True,
        necessite_validation=True,
        niveaux_validation=1
    )
    db_session.add(type_conge)
    await db_session.flush()

    # Create a solde for the employee
    solde = SoldeConge(
        employe_id=1,
        type_conge_id=type_conge.id,
        annee=2024,
        alloue=25.0,
        utilise=0.0,
        restant=25.0,
        reporte=0.0
    )
    db_session.add(solde)
ession.flush()

    # Create a demande
    demande = DemandeConge(
        employe_id=1,
        type_conge_id=type_conge.id,
        date_debut=date(2024, 3, 1),
        date_fin=date(2024, 3, 5),
        est_demi_journee=False,
        periode_demi_journee=None,
        nb_jours_demandes=5.0,
        nb_jours_ouvrables=5.0,
        raison="Vacances familiales",
        statut=StatutDemande.PENDING.value,
        niveau_validation_actuel=0
    )
    db_session.add(demande)
    await db_session.flush()
_session.commit()

    demande_id = demande.id

    # Approve at level 1 (should be final approval)
    result = await ValidationService.approve_at_level(
        demande_id=demande_id,
        valideur_id=100,
        commentaire="Approuvé",
        db=db_session
    )

    # Verify the demande status
    assert result.statut == StatutDemande.APPROVED.value
    assert result.niveau_validation_actuel == 1
    assert result.date_decision_finale is not None

    # Verify the solde was deducted
    await db_session.refresh(solde)
    assert solde.utilise == 5.0
    assert solde.restant == 20.0

    # Verify historique was created
    stmt = select(HistoriqueConge).where(
        HistoriqueConge.demande_conge_id == demande_id
    )
    result_hist = await db_session.execute(stmt)
    historique = result_hist.scalar_one()

    assert historique.niveau_validation == 1
    assert historique.valideur_id == 100
    assert historique.action == ActionHistorique.APPROVED.value
    assert historique.commentaire == "Approuvé"


@pytest.mark.asyncio
async def test_approve_at_level_multi_level_first_approval(
    db_session: AsyncSession
):
    """Test first approval when there are multiple validation levels"""
    # Create a type de congé with 3 validation levels
    type_conge = TypeConge(
        nom="Congé Spécial",
        code="CS",
        nb_jours_max_par_an=10.0,
        report_autorise=False,
     ation=True,
        niveaux_validation=3
    )
    db_session.add(type_conge)
    await db_session.flush()

    # Create a solde for the employee
    solde = SoldeConge(
        employe_id=2,
        type_conge_id=type_conge.id,
        annee=2024,
        alloue=10.0,
        utilise=0.0,
        restant=10.0,
        reporte=0.0
    )
    db_session.add(solde)
    await db_session.flush()

    # Create a demande
    demande = DemandeConge(
        employe_id=2,
        type_conge_id=type_conge.id,
raises(ValueError, match="ne peut être validée"):
        await ValidationService.approve_at_level(
            demande_id=demande.id,
            valideur_id=100,
            commentaire="Test",
            db=db_session
        )
h()

    # Create a demande with APPROVED status
    demande = DemandeConge(
        employe_id=4,
        type_conge_id=type_conge.id,
        date_debut=date(2024, 6, 1),
        date_fin=date(2024, 6, 1),
        est_demi_journee=False,
        nb_jours_demandes=1.0,
        nb_jours_ouvrables=1.0,
        raison="Test",
        statut=StatutDemande.APPROVED.value,
        niveau_validation_actuel=1
    )
    db_session.add(demande)
    await db_session.flush()
    await db_session.commit()

    with pytest.validation=1
    )
    db_session.add(type_conge)
    await db_session.flusror, match="Demande 999 non trouvée"):
        await ValidationService.approve_at_level(
            demande_id=999,
            valideur_id=100,
            commentaire="Test",
            db=db_session
        )


@pytest.mark.asyncio
async def test_approve_at_level_invalid_status(db_session: AsyncSession):
    """Test error when demande has invalid status"""
    # Create a type de congé
    type_conge = TypeConge(
        nom="Congé Test",
        code="CT",
        nb_jours_max_par_an=10.0,
        niveaux_exist"""
    with pytest.raises(ValueErl",
        db=db_session
    )

    # Verify the demande status is APPROVED
    assert result.statut == StatutDemande.APPROVED.value
    assert result.niveau_validation_actuel == 2
    assert result.date_decision_finale is not None

    # Verify the solde was deducted (0.5 days)
    await db_session.refresh(solde)
    assert solde.utilise == 2.5
    assert solde.restant == 9.5


@pytest.mark.asyncio
async def test_approve_at_level_demande_not_found(db_session: AsyncSession):
    """Test error when demande doesn't  = await ValidationService.approve_at_level(
        demande_id=demande_id,
        valideur_id=102,
        commentaire="Approuvé niveau 2 - finaconge.id,
        date_debut=date(2024, 5, 10),
        date_fin=date(2024, 5, 10),
        est_demi_journee=True,
        periode_demi_journee="MATIN",
        nb_jours_demandes=0.5,
        nb_jours_ouvrables=0.5,
        raison="Rendez-vous médical",
        statut=StatutDemande.IN_PROGRESS.value,
        niveau_validation_actuel=1
    )
    db_session.add(demande)
    await db_session.flush()
    await db_session.commit()

    demande_id = demande.id

    # Approve at level 2 (final approval)
    resultion=True,
        niveaux_validation=2
    )
    db_session.add(type_conge)
    await db_session.flush()

    # Create a solde for the employee
    solde = SoldeConge(
        employe_id=3,
        type_conge_id=type_conge.id,
        annee=2024,
        alloue=12.0,
        utilise=2.0,
        restant=10.0,
        reporte=0.0
    )
    db_session.add(solde)
    await db_session.flush()

    # Create a demande already at level 1
    demande = DemandeConge(
        employe_id=3,
        type_conge_id=type_   code="RTT",
        nb_jours_max_par_an=12.0,
        report_autorise=True,
        necessite_validatsert result.niveau_validation_actuel == 1
    assert result.date_decision_finale is None

    # Verify the solde was NOT deducted yet
    await db_session.refresh(solde)
    assert solde.utilise == 0.0
    assert solde.restant == 10.0


@pytest.mark.asyncio
async def test_approve_at_level_multi_level_final_approval(
    db_session: AsyncSession
):
    """Test final approval in multi-level validation"""
    # Create a type de congé with 2 validation levels
    type_conge = TypeConge(
        nom="RTT",
     PROGRESS
    assert result.statut == StatutDemande.IN_PROGRESS.value
    asuvrables=3.0,
        raison="Congé spécial",
        statut=StatutDemande.PENDING.value,
        niveau_validation_actuel=0
    )
    db_session.add(demande)
    await db_session.flush()
    await db_session.commit()

    demande_id = demande.id

    # Approve at level 1 (should move to IN_PROGRESS)
    result = await ValidationService.approve_at_level(
        demande_id=demande_id,
        valideur_id=101,
        commentaire="Approuvé niveau 1",
        db=db_session
    )

    # Verify the demande status is IN_e=False,
        periode_demi_journee=None,
        nb_jours_demandes=3.0,
        nb_jours_o        date_debut=date(2024, 4, 1),
        date_fin=date(2024, 4, 3),
        est_demi_journe
