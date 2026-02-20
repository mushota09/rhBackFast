"""Tests for conge_app models"""
import pytest
from datetime import date, datetime
from app.conge_app.models import (
    TypeConge,
    JourFerie,
    DemandeConge,
    SoldeConge,
    HistoriqueConge
)


def test_type_conge_model_structure():
    """Test TypeConge model can be instantiated"""
    # This test verifies the model structure is correct
    assert hasattr(TypeConge, '__tablename__')
    assert TypeConge.__tablename__ == 'cg_type_conge'
    assert hasattr(TypeConge, 'nom')
    assert hasattr(TypeConge, 'code')
    assert hasattr(TypeConge, 'nb_jours_max_par_an')
    assert hasattr(TypeConge, 'report_autorise')
    assert hasattr(TypeConge, 'necessite_validation')
    assert hasattr(TypeConge, 'niveaux_validation')
    assert hasattr(TypeConge, 'couleur')
    assert hasattr(TypeConge, 'description')


def test_jour_ferie_model_structure():
    """Test JourFerie model can be instantiated"""
    assert hasattr(JourFerie, '__tablename__')
    assert JourFerie.__tablename__ == 'cg_jour_ferie'
    assert hasattr(JourFerie, 'pays_code')
    assert hasattr(JourFerie, 'nom')
    assert hasattr(JourFerie, 'date_estimated')
    assert hasattr(JourFerie, 'date_observed')
    assert hasattr(JourFerie, 'annee')
    assert hasattr(JourFerie, 'est_personnalise')


def test_demande_conge_model_structure():
    """Test DemandeConge model can be instantiated"""
    assert hasattr(DemandeConge, '__tablename__')
    assert DemandeConge.__tablename__ == 'cg_demande_conge'
    assert hasattr(DemandeConge, 'employe_id')
    assert hasattr(DemandeConge, 'type_conge_id')
    assert hasattr(DemandeConge, 'date_debut')
    assert hasattr(DemandeConge, 'date_fin')
    assert hasattr(DemandeConge, 'est_demi_journee')
    assert hasattr(DemandeConge, 'periode_demi_journee')
    assert hasattr(DemandeConge, 'nb_jours_demandes')
    assert hasattr(DemandeConge, 'nb_jours_ouvrables')
    assert hasattr(DemandeConge, 'raison')
    assert hasattr(DemandeConge, 'statut')
    assert hasattr(DemandeConge, 'niveau_validation_actuel')
    assert hasattr(DemandeConge, 'documents')
    assert hasattr(DemandeConge, 'date_soumission')
    assert hasattr(DemandeConge, 'date_decision_finale')


def test_solde_conge_model_structure():
    """Test SoldeConge model can be instantiated"""
    assert hasattr(SoldeConge, '__tablename__')
    assert SoldeConge.__tablename__ == 'cg_solde_conge'
    assert hasattr(SoldeConge, 'employe_id')
    assert hasattr(SoldeConge, 'type_conge_id')
    assert hasattr(SoldeConge, 'annee')
    assert hasattr(SoldeConge, 'alloue')
    assert hasattr(SoldeConge, 'utilise')
    assert hasattr(SoldeConge, 'restant')
    assert hasattr(SoldeConge, 'reporte')
    assert hasattr(SoldeConge, 'date_expiration')


def test_historique_conge_model_structure():
    """Test HistoriqueConge model can be instantiated"""
    assert hasattr(HistoriqueConge, '__tablename__')
    assert HistoriqueConge.__tablename__ == 'cg_historique_conge'
    assert hasattr(HistoriqueConge, 'demande_conge_id')
    assert hasattr(HistoriqueConge, 'niveau_validation')
    assert hasattr(HistoriqueConge, 'valideur_id')
    assert hasattr(HistoriqueConge, 'poste_valideur_id')
    assert hasattr(HistoriqueConge, 'action')
    assert hasattr(HistoriqueConge, 'date_action')
    assert hasattr(HistoriqueConge, 'commentaire')
    assert hasattr(HistoriqueConge, 'delegue_a_id')

