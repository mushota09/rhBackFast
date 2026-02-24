"""Test for DELETE /api/conge/demandes/{id} endpoint."""
import pytest
from datetime import date
from sqlalchemy import select
from app.conge_app.models import DemandeConge, TypeConge, SoldeConge
from app.conge_app.constants import StatutDemande
from app.user_app.models import Employe


@pytest.mark.asyncio
async def test_cancel_demande_service(db_session):
    """Test the cancel_demande service method."""
    from app.conge_app.services import DemandeCongeService

    # Create a type de congé
    type_conge = TypeConge(
        nom="Congé Payé",
        code="CP",
        nb_jours_max_par_an=25.0,
        report_autorise=True,
        necessite_validation=True,
        niveaux_validation=2
    )
    db_session.add(type_conge)
    await db_session.flush()

    # Create an employee (simplified - assuming Employe model exists)
    # Note: This might need adjustment based on actual Employe model
    employe = Employe(
        nom="Test",
        prenom="User",
        email="test@example.com",
        pays_code="CD"
    )
    db_session.add(employe)
    await db_session.flush()

    # Create a solde
    solde = SoldeConge(
        employe_id=employe.id,
        type_conge_id=type_conge.id,
        annee=2024,
        alloue=25.0,
        utilise=5.0,
        reporte=0.0,
        restant=20.0
    )
    db_session.add(solde)
    await db_session.flush()

    # Create a demande with APPROVED status
    demande = DemandeConge(
        employe_id=employe.id,
        type_conge_id=type_conge.id,
        date_debut=date(2024, 6, 1),
        date_fin=date(2024, 6, 5),
        est_demi_journee=False,
        periode_demi_journee=None,
        nb_jours_demandes=5.0,
        nb_jours_ouvrables=5.0,
        raison="Vacances d'été",
        statut=StatutDemande.APPROVED.value,
        niveau_validation_actuel=2
    )
    db_session.add(demande)
    await db_session.commit()

    # Test cancel_demande
    cancelled_demande = await DemandeCongeService.cancel_demande(
        demande_id=demande.id,
        user_id=1,  # Mock user ID
        db=db_session
    )

    # Verify the demande is cancelled
    assert cancelled_demande.statut == StatutDemande.CANCELLED.value

    # Verify the solde is restored
    stmt = select(SoldeConge).where(
        SoldeConge.employe_id == employe.id,
        SoldeConge.type_conge_id == type_conge.id,
        SoldeConge.annee == 2024
    )
    result = await db_session.execute(stmt)
    updated_solde = result.scalar_one()

    # The utilise should be back to 0 (5.0 - 5.0)
    assert updated_solde.utilise == 0.0
    assert updated_solde.restant == 25.0  # alloue (25) - utilise (0) + reporte (0)


@pytest.mark.asyncio
async def test_cancel_pending_demande(db_session):
    """Test cancelling a PENDING demande (no balance restoration needed)."""
    from app.conge_app.services import DemandeCongeService

    # Create a type de congé
    type_conge = TypeConge(
        nom="Congé Payé",
        code="CP2",
        nb_jours_max_par_an=25.0,
        report_autorise=True,
        necessite_validation=True,
        niveaux_validation=2
    )
    db_session.add(type_conge)
    await db_session.flush()

    # Create an employee
    employe = Employe(
        nom="Test2",
        prenom="User2",
        email="test2@example.com",
        pays_code="CD"
    )
    db_session.add(employe)
    await db_session.flush()

    # Create a demande with PENDING status
    demande = DemandeConge(
        employe_id=employe.id,
        type_conge_id=type_conge.id,
        date_debut=date(2024, 7, 1),
        date_fin=date(2024, 7, 3),
        est_demi_journee=False,
        periode_demi_journee=None,
        nb_jours_demandes=3.0,
        nb_jours_ouvrables=3.0,
        raison="Congé personnel",
        statut=StatutDemande.PENDING.value,
        niveau_validation_actuel=0
    )
    db_session.add(demande)
    await db_session.commit()

    # Test cancel_demande
    cancelled_demande = await DemandeCongeService.cancel_demande(
        demande_id=demande.id,
        user_id=1,
        db=db_session
    )

    # Verify the demande is cancelled
    assert cancelled_demande.statut == StatutDemande.CANCELLED.value


@pytest.mark.asyncio
async def test_cancel_nonexistent_demande(db_session):
    """Test cancelling a non-existent demande raises ValueError."""
    from app.conge_app.services import DemandeCongeService

    with pytest.raises(ValueError, match="Demande .* non trouvée"):
        await DemandeCongeService.cancel_demande(
            demande_id=99999,
            user_id=1,
            db=db_session
        )
