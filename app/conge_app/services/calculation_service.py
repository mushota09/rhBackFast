"""Service pour les calculs de congés"""
from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conge_app.models import SoldeConge, DemandeConge
from app.conge_app.utils import is_weekend, count_working_days, dates_overlap
from app.conge_app.services.holiday_service import HolidayService


class CongeCalculationService:
    """Service pour les calculs de congés"""

    @staticmethod
    async def calculate_working_days(
        date_debut: date,
        date_fin: date,
        est_demi_journee: bool,
        periode_demi_journee: Optional[str],
        pays_code: str,
        db: AsyncSession
    ) -> Tuple[float, float]:
        """
        Calcule les joursdemandés et les jours ouvrables.

        Args:
            date_debut: Date de début
            date_fin: Date de fin
            est_demi_journee: Si c'est une demi-journée
            periode_demi_journee: Période (MATIN ou APRES_MIDI)
            pays_code: Code ISO du pays
            db: Session de base de données

        Returns:
            Tuple (nb_jours_demandes, nb_jours_ouvrables)

        Raises:
            ValueError: Si les dates ou paramètres sont invalides
        """
        if date_fin < date_debut:
            raise ValueError("Date fin doit être >= date début")

        if est_demi_journee:
            if date_debut != date_fin:
                raise ValueError(
                    "Demi-journée: dates doivent être identiques"
                )
            valid_periods = ["MATIN", "APRES_MIDI"]
            if (not periode_demi_journee or
                    periode_demi_journee not in valid_periods):
                raise ValueError(
                    "periode_demi_journee doit être MATIN ou APRES_MIDI"
                )
            nb_jours_demandes = 0.5
        else:
            if periode_demi_journee:
                raise ValueError(
                    "Jours complets: periode_demi_journee doit être None"
                )
            days_diff = (date_fin - date_debut).days + 1
            nb_jours_demandes = float(days_diff)

        holiday_dates = await HolidayService.get_holidays_between_dates(
            pays_code=pays_code,
            date_debut=date_debut,
            date_fin=date_fin,
            db=db
        )

        if est_demi_journee:
            if is_weekend(date_debut) or date_debut in holiday_dates:
                nb_jours_ouvrables = 0.0
            else:
                nb_jours_ouvrables = 0.5
        else:
            working_days_count = count_working_days(
                date_debut=date_debut,
                date_fin=date_fin,
                holidays=holiday_dates
            )
            nb_jours_ouvrables = float(working_days_count)

        return nb_jours_demandes, nb_jours_ouvrables

    @staticmethod
    async def check_sufficient_balance(
        employe_id: int,
        type_conge_id: int,
        nb_jours_demandes: float,
        annee: int,
        db: AsyncSession
    ) -> Tuple[bool, Optional[float]]:
        """
        Vérifie si l'employé a un solde suffisant.

        Args:
            employe_id: ID de l'employé
            type_conge_id: ID du type de congé
            nb_jours_demandes: Nombre de jours demandés
            annee: Année du solde
            db: Session de base de données

        Returns:
            Tuple (has_sufficient, solde_restant)
        """
        stmt = select(SoldeConge).where(
            SoldeConge.employe_id == employe_id,
            SoldeConge.type_conge_id == type_conge_id,
            SoldeConge.annee == annee
        )
        result = await db.execute(stmt)
        solde = result.scalar_one_or_none()

        if not solde:
            return False, None

        has_sufficient = solde.restant >= nb_jours_demandes
        return has_sufficient, solde.restant

    @staticmethod
    async def check_date_conflicts(
        employe_id: int,
        date_debut: date,
        date_fin: date,
        exclude_demande_id: Optional[int],
        db: AsyncSession
    ) -> List[DemandeConge]:
        """
        Vérifie les conflits de dates avec d'autres demandes approuvées.

        Args:
            employe_id: ID de l'employé
            date_debut: Date de début
            date_fin: Date de fin
            exclude_demande_id: ID de demande à exclure (pour updates)
            db: Session de base de données

        Returns:
            Liste des demandes en conflit
        """
        stmt = select(DemandeConge).where(
            DemandeConge.employe_id == employe_id,
            DemandeConge.statut == "APPROVED"
        )

        if exclude_demande_id:
            stmt = stmt.where(DemandeConge.id != exclude_demande_id)

        result = await db.execute(stmt)
        approved_demandes = result.scalars().all()

        conflicts = []
        for demande in approved_demandes:
            if dates_overlap(
                date_debut, date_fin,
                demande.date_debut, demande.date_fin
            ):
                conflicts.append(demande)

        return conflicts

