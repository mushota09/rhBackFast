"""Constantes du workflow paie.

Le moteur de workflow est celui mis en place par ``conge_app`` : les mêmes
tables génériques (`cg_statut_processus`, `cg_etape_processus`,
`cg_action_etape_processus`, `cg_demande_attribution`, `cg_historique_demande`)
sont réutilisées.

La paie est polymorphiquement identifiée par ``demande_type = 'PERIODE_PAIE'``
et ``code_processus = 'PAIE'``.
"""
from __future__ import annotations

from enum import Enum


class CodeProcessusPaie(str, Enum):
    """Code de processus associé à la paie."""

    PAIE = "PAIE"


class DemandeTypePaie(str, Enum):
    """Type de demande utilisé dans les tables polymorphiques."""

    PERIODE_PAIE = "PERIODE_PAIE"


class CodeStatutPaie(str, Enum):
    """Statuts globaux spécifiques au workflow paie.

    On réutilise les statuts génériques du module congé (``EN_ATTENTE``,
    ``EN_COURS``, ``VALIDE``, ``REJETE``, ``ANNULE``) et on ajoute les
    statuts métier paie.
    """

    EN_ATTENTE = "EN_ATTENTE"
    EN_COURS = "EN_COURS"
    VALIDE = "VALIDE"
    REJETE = "REJETE"
    ANNULE = "ANNULE"
    EN_MODIFICATION = "EN_MODIFICATION"
    PAYE = "PAYE"


class NomActionPaie(str, Enum):
    """Actions applicables sur les étapes du workflow paie."""

    APPROUVER = "APPROUVER"
    REJETER = "REJETER"
    DEMANDER_MODIF = "DEMANDER_MODIF"
    PRET_A_VALIDER = "PRET_A_VALIDER"
    MARQUER_PAYE = "MARQUER_PAYE"


# Statut texte rétro-compat synchronisé sur ``PeriodePaie.statut``
# lors des transitions workflow.
STATUT_TEXTUEL_PAR_CODE: dict[str, str] = {
    CodeStatutPaie.EN_ATTENTE.value: "PROCESSING",
    CodeStatutPaie.EN_COURS.value: "PROCESSING",
    CodeStatutPaie.EN_MODIFICATION.value: "PROCESSING",
    CodeStatutPaie.VALIDE.value: "APPROVED",
    CodeStatutPaie.REJETE.value: "DRAFT",
    CodeStatutPaie.ANNULE.value: "DRAFT",
    CodeStatutPaie.PAYE.value: "PAID",
}


# Permissions spécifiques au workflow paie.
WORKFLOW_PERMISSIONS: dict[str, str] = {
    "paie_workflow.submit": "Soumettre une période de paie au workflow",
    "paie_workflow.approve": "Valider / rejeter une étape du workflow paie",
    "paie_workflow.manage": "Gérer la configuration du workflow paie",
}
