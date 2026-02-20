"""Leave management constants and enumerations"""
from enum import Enum


class DemiJournee(str, Enum):
    """Half-day period enumeration"""
    MATIN = "MATIN"
    APRES_MIDI = "APRES_MIDI"
    JOURNEE_COMPLETE = "JOURNEE_COMPLETE"


class StatutDemande(str, Enum):
    """Leave request status enumeration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ActionHistorique(str, Enum):
    """History action enumeration"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DELEGATED = "DELEGATED"


class TypeDateFerie(str, Enum):
    """Holiday date type enumeration"""
    NORMAL = "NORMAL"  # Date normale (fixe)
    ESTIMATED = "ESTIMATED"  # Date estimée (fêtes lunaires)
    OBSERVED = "OBSERVED"  # Date observée (reportée si weekend)


# Supported countries (extensible)
PAYS_SUPPORTES = {
    "CD": "République Démocratique du Congo",
    "FR": "France",
    "BE": "Belgique",
    "CA": "Canada",
    "US": "United States",
    "GB": "United Kingdom",
    "DE": "Germany",
    "ES": "Spain",
    "IT": "Italy",
    "NL": "Netherlands",
    "CH": "Switzerland",
    "LU": "Luxembourg",
    "BI": "Burundi",
}

# Permissions for leave management
PERMISSIONS = {
    "conge.view": "Consulter les congés",
    "conge.create": "Créer des demandes de congés",
    "conge.update": "Modifier des demandes de congés",
    "conge.delete": "Supprimer des demandes de congés",
    "conge.approve": "Approuver des demandes de congés",
    "conge.manage_types": "Gérer les types de congés",
    "conge.manage_soldes": "Gérer les soldes de congés",
    "conge.export": "Exporter les données de congés",
}

# Default configuration values
DEFAULT_COUNTRY_CODE = "BI"
HOLIDAYS_AUTO_LOAD = True
MAX_VALIDATION_LEVELS = 5
MAX_DOCUMENT_SIZE_MB = 5
ALLOWED_DOCUMENT_TYPES = ["pdf", "jpg", "jpeg", "png"]

# Pagination defaults
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000


