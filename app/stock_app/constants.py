"""Constants and enumerations for the stock management module.

Toutes les valeurs énumérées ici sont des **valeurs par défaut** seedées par
:mod:`app.stock_app.init_data`. Le workflow réel (statuts, étapes, actions)
reste piloté par les tables ``cg_*`` et reste donc 100% configurable en DB
après initialisation.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict


class CodeProcessusStock(str, Enum):
    """Codes de processus workflow gérés par le module stock.

    Stockés dans ``cg_etape_processus.code_processus``.
    """

    SORTIE = "STOCK_SORTIE"
    ENTREE = "STOCK_ENTREE"
    AJUSTEMENT = "STOCK_AJUSTEMENT"


class DemandeTypeStock(str, Enum):
    """Type polymorphique pour ``cg_demande_attribution`` / ``cg_historique_demande``."""

    DEMANDE_STOCK = "DEMANDE_STOCK"


class CodeStatutStock(str, Enum):
    """Statuts globaux par défaut du workflow stock (``cg_statut_processus``).

    Réutilise les statuts génériques déjà seedés par ``conge_app``.
    """

    EN_ATTENTE = "EN_ATTENTE"
    EN_COURS = "EN_COURS"
    VALIDE = "VALIDE"
    REJETE = "REJETE"
    ANNULE = "ANNULE"


class NomActionStock(str, Enum):
    """Noms d'actions par défaut applicables sur les étapes stock."""

    APPROUVER = "APPROUVER"
    REJETER = "REJETER"
    CONFIRMER_LIVRAISON = "CONFIRMER_LIVRAISON"


class TypeMouvement(str, Enum):
    """Sens d'un mouvement de stock."""

    ENTREE = "ENTREE"
    SORTIE = "SORTIE"
    AJUSTEMENT = "AJUSTEMENT"


class StatutAttribution(str, Enum):
    """Statut d'une ligne ``cg_demande_attribution`` (rappel, dupliqué pour découplage)."""

    EN_ATTENTE = "en_attente"
    PRISE_EN_CHARGE = "prise_en_charge"
    TRAITEE = "traitee"


# Permissions applicatives du module stock (custom).
PERMISSIONS: Dict[str, str] = {
    "stock.view": "Consulter le stock",
    "stock.manage_articles": "Gérer les articles, catégories et unités",
    "stock.create_demande": "Créer une demande de stock",
    "stock.approve_demande": "Approuver / rejeter une demande de stock",
    "stock.manage_workflow": "Gérer le workflow stock (étapes, actions, statuts)",
    "stock.view_attributions": "Voir les attributions matériel par employé",
}
