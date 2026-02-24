"""Service pour la gestion des demandes de congé"""
from datetime import date
from typing import Optional, List, Tuple, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

from app.conge_app.models import DemandeConge

if TYPE_CHECKING:
    from app.conge_app.schemas import DemandeCongeCreate, DemandeCongeUpdate


class DemandeCongeService:
    """Service pour la gestion des demandes de congé"""

    @staticmethod
    async def create_demande(
        demande_data: 'DemandeCongeCreate',
        db: AsyncSession
    ) -> DemandeConge:
        """
        Crée une nouvelle demande de congé.

        Args:
            demande_data: Données de la demande (schéma Pydantic)
            db: Session de base de données

        Returns:
            La demande créée

        Raises:
            ValueError: Si les validations échouent
        """
        from sqlalchemy import select
        from app.user_app.models import Employe
        from app.conge_app.models import TypeConge
        from app.conge_app.services.calculation_service import (
            CongeCalculationService
        )
        from app.conge_app.constants import StatutDemande

        # Extraire les données du schéma
        employe_id = demande_data.employe_id
        type_conge_id = demande_data.type_conge_id
        date_debut = demande_data.date_debut
        date_fin = demande_data.date_fin
        est_demi_journee = demande_data.est_demi_journee
        periode_demi_journee = demande_data.periode_demi_journee
        raison = demande_data.raison

        # 1. Valider que l'employé existe
        stmt = select(Employe).where(Employe.id == employe_id)
        result = await db.execute(stmt)
        employe = result.scalar_one_or_none()

        if not employe:
            raise ValueError(f"Employé {employe_id} non trouvé")

        # Récupérer le pays de l'employé (par défaut CD)
        pays_code = getattr(employe, 'pays_code', 'CD')

        # 2. Valider que le type de congé existe
        stmt = select(TypeConge).where(TypeConge.id == type_conge_id)
        result = await db.execute(stmt)
        type_conge = result.scalar_one_or_none()

        if not type_conge:
            raise ValueError(f"Type de congé {type_conge_id} non trouvé")

        # 3. Valider date_debut <= date_fin
        if date_debut > date_fin:
            raise ValueError(
                "La date de début doit être inférieure ou égale à la date de fin"
            )

        # 4. Calculer nb_jours_demandes et nb_jours_ouvrables
        nb_jours_demandes, nb_jours_ouvrables = (
            await CongeCalculationService.calculate_working_days(
                date_debut=date_debut,
                date_fin=date_fin,
                est_demi_journee=est_demi_journee,
                periode_demi_journee=periode_demi_journee,
                pays_code=pays_code,
                db=db
            )
        )

        # 5. Vérifier solde suffisant
        annee = date_debut.year
        has_sufficient, solde_restant = (
            await CongeCalculationService.check_sufficient_balance(
                employe_id=employe_id,
                type_conge_id=type_conge_id,
                nb_jours_demandes=nb_jours_demandes,
                annee=annee,
                db=db
            )
        )

        if not has_sufficient:
            if solde_restant is None:
                raise ValueError(
                    f"Aucun solde trouvé pour l'employé {employe_id} "
                    f"et le type de congé {type_conge_id} pour l'année {annee}"
                )
            raise ValueError(
                f"Solde insuffisant. Solde restant: {solde_restant} jours, "
                f"demandé: {nb_jours_demandes} jours"
            )

        # 6. Vérifier pas de conflit de dates
        conflicts = await CongeCalculationService.check_date_conflicts(
            employe_id=employe_id,
            date_debut=date_debut,
            date_fin=date_fin,
            exclude_demande_id=None,
            db=db
        )

        if conflicts:
            conflict_dates = [
                f"{c.date_debut} - {c.date_fin}" for c in conflicts
            ]
            raise ValueError(
                f"Conflit de dates avec des demandes approuvées existantes: "
                f"{', '.join(conflict_dates)}"
            )

        # 7. Créer la demande avec statut=PENDING
        demande = DemandeConge(
            employe_id=employe_id,
            type_conge_id=type_conge_id,
            date_debut=date_debut,
            date_fin=date_fin,
            est_demi_journee=est_demi_journee,
            periode_demi_journee=periode_demi_journee,
            nb_jours_demandes=nb_jours_demandes,
            nb_jours_ouvrables=nb_jours_ouvrables,
            raison=raison,
            statut=StatutDemande.PENDING.value,
            niveau_validation_actuel=0,
            documents=demande_data.documents
        )

        db.add(demande)
        await db.commit()
        await db.refresh(demande)

        return demande

    @staticmethod
    async def update_demande(
        demande_id: int,
        demande_data: 'DemandeCongeUpdate',
        db: AsyncSession
    ) -> DemandeConge:
        """
        Met à jour une demande de congé.

        Args:
            demande_id: ID de la demande
            demande_data: Données de mise à jour (schéma Pydantic)
            db: Session de base de données

        Returns:
            La demande mise à jour

        Raises:
            ValueError: Si la demande ne peut être modifiée
        """
        from sqlalchemy import select
        from app.user_app.models import Employe
        from app.conge_app.services.calculation_service import (
            CongeCalculationService
        )
        from app.conge_app.constants import StatutDemande

        # Récupérer la demande existante
        stmt = select(DemandeConge).where(DemandeConge.id == demande_id)
        result = await db.execute(stmt)
        demande = result.scalar_one_or_none()

        if not demande:
            raise ValueError(f"Demande {demande_id} non trouvée")

        # 1. Vérifier statut=PENDING (seulement modifiable si en attente)
        if demande.statut != StatutDemande.PENDING.value:
            raise ValueError(
                f"La demande ne peut être modifiée car son statut est "
                f"{demande.statut}. Seules les demandes en attente (PENDING) "
                f"peuvent être modifiées."
            )

        # Extraire les nouvelles valeurs du schéma
        date_debut = demande_data.date_debut
        date_fin = demande_data.date_fin
        est_demi_journee = demande_data.est_demi_journee
        periode_demi_journee = demande_data.periode_demi_journee
        raison = demande_data.raison

        # Déterminer si les dates changent
        dates_changed = False
        new_date_debut = date_debut if date_debut is not None else demande.date_debut
        new_date_fin = date_fin if date_fin is not None else demande.date_fin
        new_est_demi_journee = (
            est_demi_journee if est_demi_journee is not None
            else demande.est_demi_journee
        )
        new_periode_demi_journee = (
            periode_demi_journee if periode_demi_journee is not None
            else demande.periode_demi_journee
        )

        if (new_date_debut != demande.date_debut or
            new_date_fin != demande.date_fin or
            new_est_demi_journee != demande.est_demi_journee or
            new_periode_demi_journee != demande.periode_demi_journee):
            dates_changed = True

        # 2. Recalculer jours si dates changent
        if dates_changed:
            # Valider les nouvelles dates
            if new_date_debut > new_date_fin:
                raise ValueError(
                    "La date de début doit être inférieure ou égale à "
                    "la date de fin"
                )

            # Récupérer le pays de l'employé
            stmt_employe = select(Employe).where(
                Employe.id == demande.employe_id
            )
            result_employe = await db.execute(stmt_employe)
            employe = result_employe.scalar_one_or_none()
            pays_code = getattr(employe, 'pays_code', 'CD') if employe else 'CD'

            # Recalculer les jours
            nb_jours_demandes, nb_jours_ouvrables = (
                await CongeCalculationService.calculate_working_days(
                    date_debut=new_date_debut,
                    date_fin=new_date_fin,
                    est_demi_journee=new_est_demi_journee,
                    periode_demi_journee=new_periode_demi_journee,
                    pays_code=pays_code,
                    db=db
                )
            )

            # Vérifier solde suffisant avec les nouvelles valeurs
            annee = new_date_debut.year
            has_sufficient, solde_restant = (
                await CongeCalculationService.check_sufficient_balance(
                    employe_id=demande.employe_id,
                    type_conge_id=demande.type_conge_id,
                    nb_jours_demandes=nb_jours_demandes,
                    annee=annee,
                    db=db
                )
            )

            if not has_sufficient:
                if solde_restant is None:
                    raise ValueError(
                        f"Aucun solde trouvé pour l'employé "
                        f"{demande.employe_id} et le type de congé "
                        f"{demande.type_conge_id} pour l'année {annee}"
                    )
                raise ValueError(
                    f"Solde insuffisant. Solde restant: {solde_restant} jours, "
                    f"demandé: {nb_jours_demandes} jours"
                )

            # Vérifier pas de conflit de dates (en excluant cette demande)
            conflicts = await CongeCalculationService.check_date_conflicts(
                employe_id=demande.employe_id,
                date_debut=new_date_debut,
                date_fin=new_date_fin,
                exclude_demande_id=demande_id,
                db=db
            )

            if conflicts:
                conflict_dates = [
                    f"{c.date_debut} - {c.date_fin}" for c in conflicts
                ]
                raise ValueError(
                    f"Conflit de dates avec des demandes approuvées "
                    f"existantes: {', '.join(conflict_dates)}"
                )

            # Mettre à jour les champs de dates et jours
            demande.date_debut = new_date_debut
            demande.date_fin = new_date_fin
            demande.est_demi_journee = new_est_demi_journee
            demande.periode_demi_journee = new_periode_demi_journee
            demande.nb_jours_demandes = nb_jours_demandes
            demande.nb_jours_ouvrables = nb_jours_ouvrables

        # Mettre à jour la raison si fournie
        if raison is not None:
            demande.raison = raison

        # Mettre à jour les documents si fournis
        if demande_data.documents is not None:
            demande.documents = demande_data.documents

        await db.commit()
        await db.refresh(demande)

        return demande

    @staticmethod
    async def cancel_demande(
        demande_id: int,
        user_id: int,
        db: AsyncSession
    ) -> DemandeConge:
        """
        Annule une demande de congé.

        Args:
            demande_id: ID de la demande
            user_id: ID de l'utilisateur qui annule la demande
            db: Session de base de données

        Returns:
            La demande annulée

        Raises:
            ValueError: Si la demande n'existe pas
        """
        from sqlalchemy import select
        from app.conge_app.models import SoldeConge
        from app.conge_app.constants import StatutDemande

        # Récupérer la demande existante
        stmt = select(DemandeConge).where(DemandeConge.id == demande_id)
        result = await db.execute(stmt)
        demande = result.scalar_one_or_none()

        if not demande:
            raise ValueError(f"Demande {demande_id} non trouvée")

        # 1. Statut=CANCELLED
        old_statut = demande.statut
        demande.statut = StatutDemande.CANCELLED.value

        # 2. Restaurer solde si déjà déduit (si la demande était APPROVED)
        if old_statut == StatutDemande.APPROVED.value:
            annee = demande.date_debut.year
            stmt_solde = select(SoldeConge).where(
                SoldeConge.employe_id == demande.employe_id,
                SoldeConge.type_conge_id == demande.type_conge_id,
                SoldeConge.annee == annee
            )
            result_solde = await db.execute(stmt_solde)
            solde = result_solde.scalar_one_or_none()

            if solde:
                # Restaurer le solde en soustrayant de utilise
                solde.utilise -= demande.nb_jours_demandes
                solde.restant = solde.alloue - solde.utilise + solde.reporte

        await db.commit()
        await db.refresh(demande)

        return demande

    @staticmethod
    async def list_demandes(
        filters: dict,
        expand: Optional[str],
        skip: int,
        limit: Optional[int],
        no_pagination: bool,
        search: Optional[str],
        ordering: Optional[str],
        db: AsyncSession
    ) -> Tuple[List[DemandeConge], int]:
        """
        Liste les demandes de congé avec filtres et pagination.

        Args:
            filters: Dictionnaire de filtres (employe_id, type_conge_id, etc.)
            expand: Relations à charger (séparées par virgules)
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner (None = tous)
            no_pagination: Si True, retourne tous les résultats
            search: Recherche dans raison et statut
            ordering: Champ de tri (préfixe - pour descendant)
            db: Session de base de données

        Returns:
            Tuple (liste de demandes, total)
        """
        from sqlalchemy import select, func
        from app.core.query_utils import (
            apply_search, apply_ordering, apply_expansion, parse_expand_param
        )

        # Construire la requête de base
        query = select(DemandeConge)

        # 1. Appliquer les filtres
        for field, value in filters.items():
            if value is not None and hasattr(DemandeConge, field):
                if field in ['date_debut', 'date_fin']:
                    # Pour les dates, on fait une comparaison >= ou <=
                    if field == 'date_debut':
                        query = query.where(DemandeConge.date_debut >= value)
                    else:
                        query = query.where(DemandeConge.date_fin <= value)
                else:
                    query = query.where(getattr(DemandeConge, field) == value)

        # 2. Appliquer la recherche
        search_fields = ['raison', 'statut']
        if search:
            query = apply_search(query, DemandeConge, search_fields, search)

        # 3. Appliquer le tri
        if ordering:
            query = apply_ordering(query, DemandeConge, ordering)
        else:
            # Tri par défaut: date de soumission décroissante
            query = query.order_by(DemandeConge.date_soumission.desc())

        # 4. Appliquer l'expansion des relations
        expand_fields = parse_expand_param(expand)
        if expand_fields:
            query = apply_expansion(query, DemandeConge, expand_fields)

        # 5. Compter le total
        count_query = select(func.count()).select_from(DemandeConge)

        # Appliquer les mêmes filtres pour le count
        for field, value in filters.items():
            if value is not None and hasattr(DemandeConge, field):
                if field in ['date_debut', 'date_fin']:
                    if field == 'date_debut':
                        count_query = count_query.where(
                            DemandeConge.date_debut >= value
                        )
                    else:
                        count_query = count_query.where(
                            DemandeConge.date_fin <= value
                        )
                else:
                    count_query = count_query.where(
                        getattr(DemandeConge, field) == value
                    )

        if search:
            count_query = apply_search(
                count_query, DemandeConge, search_fields, search
            )

        count_result = await db.execute(count_query)
        total = count_result.scalar()

        # 6. Appliquer la pagination
        if not no_pagination and limit is not None:
            query = query.offset(skip).limit(limit)

        # 7. Exécuter la requête
        result = await db.execute(query)
        demandes = result.scalars().all()

        return list(demandes), total

