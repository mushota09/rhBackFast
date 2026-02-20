"""Service pour la gestion des jours fériés"""
from datetime import date
from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import holidays

from app.conge_app.models import JourFerie


class HolidayService:
    """Service pour la gestion des jours fériés"""

    @staticmethod
    def _parse_holiday_name(name: str) -> Tuple[str, str]:
        """
        Parse le nom d'un jour férié pour extraire le type.

        Args:
            name: Nom complet du jour férié

        Returns:
            Tuple (nom_propre, type_date)
        """
        name = name.strip()
        if "(estimated)" in name.lower():
            clean_name = name.replace("(estimated)", "").strip()
            return clean_name, "ESTIMATED"
        if "(observed)" in name.lower():
            clean_name = name.replace("(observed)", "").strip()
            return clean_name, "OBSERVED"
        return name, "NORMAL"

    @staticmethod
    async def load_holidays_for_country(
        pays_code: str,
        annee: int,
        db: AsyncSession
    ) -> None:
        """
        Charge les jours fériés d'un pays pour une année donnée.

        Args:
            pays_code: Code ISO du pays (ex: 'CD', 'FR', 'BE')
            annee: Année pour laquelle charger les jours fériés
            db: Session de base de données

        Raises:
            ValueError: Si le code pays n'est pas supporté
        """
        try:
            country_holidays = holidays.country_holidays(
                pays_code, years=annee
            )
        except NotImplementedError as exc:
            raise ValueError(
                f"Code pays non supporté: {pays_code}"
            ) from exc

        for date_ferie, nom_complet in country_holidays.items():
            nom_propre, type_date = HolidayService._parse_holiday_name(
                nom_complet
            )
            stmt = select(JourFerie).where(
                JourFerie.pays_code == pays_code,
                JourFerie.nom == nom_propre,
                JourFerie.annee == annee
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                jour_ferie = JourFerie(
                    pays_code=pays_code,
                    nom=nom_propre,
                    date_ferie=date_ferie,
                    type_date=type_date,
                    annee=annee,
                    est_personnalise=False
                )
                db.add(jour_ferie)
        await db.commit()

    @staticmethod
    async def get_holidays_between_dates(
        pays_code: str,
        date_debut: date,
        date_fin: date,
        db: AsyncSession
    ) -> List[date]:
        """
        Récupère les jours fériés entre deux dates.

        Args:
            pays_code: Code ISO du pays
            date_debut: Date de début
            date_fin: Date de fin
            db: Session de base de données

        Returns:
            Liste des dates de jours fériés
        """
        stmt = select(JourFerie).where(
            JourFerie.pays_code == pays_code,
            JourFerie.annee >= date_debut.year,
            JourFerie.annee <= date_fin.year
        )
        result = await db.execute(stmt)
        holidays_records = result.scalars().all()

        holiday_dates = []
        for holiday in holidays_records:
            holiday_date = holiday.date_ferie
            if holiday_date and date_debut <= holiday_date <= date_fin:
                holiday_dates.append(holiday_date)
        return holiday_dates

    @staticmethod
    async def add_custom_holiday(
        pays_code: str,
        nom: str,
        date_ferie: date,
        type_date: str,
        db: AsyncSession
    ) -> JourFerie:
        """
        Ajoute un jour férié personnalisé.

        Args:
            pays_code: Code ISO du pays
            nom: Nom du jour férié
            date_ferie: Date du jour férié
            type_date: Type de date (NORMAL, ESTIMATED, OBSERVED)
            db: Session de base de données

        Returns:
            Le jour férié créé

        Raises:
            ValueError: Si le jour férié existe déjà
        """
        annee = date_ferie.year
        stmt = select(JourFerie).where(
            JourFerie.pays_code == pays_code,
            JourFerie.nom == nom,
            JourFerie.annee == annee
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(f"Jour férié existe déjà: {nom}")

        jour_ferie = JourFerie(
            pays_code=pays_code,
            nom=nom,
            date_ferie=date_ferie,
            type_date=type_date,
            annee=annee,
            est_personnalise=True
        )
        db.add(jour_ferie)
        await db.commit()
        await db.refresh(jour_ferie)
        return jour_ferie
