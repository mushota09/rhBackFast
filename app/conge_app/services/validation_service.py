"""Service pour la validation hiérarchique des demandes de congé"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conge_app.models import (
    DemandeConge,
    HistoriqueConge,
    SoldeConge,
    TypeConge
)
from app.conge_app.constants import ActionHistorique, StatutDemande


class ValidationService:
    """Service pour la validation hiérarchique des demandes de congé"""

    @staticmethod
    async def get_required_validators(
        type_conge_id: int,
        employe_id: int,
        db: AsyncSession
    ) -> dict:
        """
        Détermine les valideurs requis pour chaque niveau de validation.

        Args:
            type_conge_id: ID du type de congé
            employe_id: ID de l'employé
            db: Session de base de données

        Returns:
            Dict avec les valideurs par niveau
            {1: [manager_id], 2: [directeur_id], 3: [rh_id]}
        """
        # TODO: Implémenter la logique de récupération des valideurs
        # selon la hiérarchie de l'employé et le type de congé
        # Pour l'instant, retourne une structure vide
        return {}

    @staticmethod
    async def can_user_validate(
        user_id: int,
        demande_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Vérifie si un utilisateur peut valider une demande.

        Args:
            user_id: ID de l'utilisateur
            demande_id: ID de la demande
            db: Session de base de données

        Returns:
            True si l'utilisateur peut valider, False sinon
        """
        # Récupérer la demande
        stmt = select(DemandeConge).where(DemandeConge.id == demande_id)
        result = await db.execute(stmt)
        demande = result.scalar_one_or_none()

        if not demande:
            return False

        # Vérifier que la demande est en attente de validation
        if demande.statut not in ["PENDING", "IN_PROGRESS"]:
            return False

        # Récupérer les valideurs requis pour le niveau actuel
        validators = await ValidationService.get_required_validators(
            type_conge_id=demande.type_conge_id,
            employe_id=demande.employe_id,
            db=db
        )

        niveau_actuel = demande.niveau_validation_actuel
        if niveau_actuel not in validators:
            return False

        # Vérifier si l'utilisateur est dans la liste des valideurs
        return user_id in validators[niveau_actuel]

    @staticmethod
    async def approve_at_level(
        demande_id: int,
        valideur_id: int,
        commentaire: Optional[str],
        db: AsyncSession
    ) -> DemandeConge:
        """
        Approuve une demande à un niveau de validation.

        Args:
            demande_id: ID de la demande
            valideur_id: ID du valideur
            commentaire: Commentaire optionnel
            db: Session de base de données

        Returns:
            La demande mise à jour

        Raises:
            ValueError: Si la demande n'existe pas ou ne peut être validée
        """
        # Récupérer la demande avec ses relations
        stmt = select(DemandeConge).where(DemandeConge.id == demande_id)
        result = await db.execute(stmt)
        demande = result.scalar_one_or_none()

        if not demande:
            raise ValueError(f"Demande {demande_id} non trouvée")

        # Vérifier que la demande peut être validée
        if demande.statut not in [
            StatutDemande.PENDING.value,
            StatutDemande.IN_PROGRESS.value
        ]:
            raise ValueError(
                f"Demande {demande_id} ne peut être validée "
                f"(statut: {demande.statut})"
            )

        # Récupérer le type de congé pour connaître le nombre de niveaux
        stmt_type = select(TypeConge).where(
            TypeConge.id == demande.type_conge_id
        )
        result_type = await db.execute(stmt_type)
        type_conge = result_type.scalar_one_or_none()

        if not type_conge:
            raise ValueError(
                f"Type de congé {demande.type_conge_id} non trouvé"
            )

        # Créer l'entrée d'historique
        historique = HistoriqueConge(
            demande_conge_id=demande_id,
            niveau_validation=demande.niveau_validation_actuel + 1,
            valideur_id=valideur_id,
            action=ActionHistorique.APPROVED.value,
            date_action=datetime.utcnow(),
            commentaire=commentaire
        )
        db.add(historique)

        # Incrémenter le niveau de validation
        demande.niveau_validation_actuel += 1

        # Vérifier si c'est le dernier niveau
        if demande.niveau_validation_actuel >= type_conge.niveaux_validation:
            # Dernier niveau: approuver définitivement
            demande.statut = StatutDemande.APPROVED.value
            demande.date_decision_finale = datetime.utcnow()

            # Déduire du solde
            annee = demande.date_debut.year
            stmt_solde = select(SoldeConge).where(
                SoldeConge.employe_id == demande.employe_id,
                SoldeConge.type_conge_id == demande.type_conge_id,
                SoldeConge.annee == annee
            )
            result_solde = await db.execute(stmt_solde)
            solde = result_solde.scalar_one_or_none()

            if solde:
                solde.utilise += demande.nb_jours_demandes
                solde.restant = (
                    solde.alloue - solde.utilise + solde.reporte
                )
            else:
                # Si pas de solde, on peut soit créer un solde négatif
                # soit lever une erreur - ici on lève une erreur
                raise ValueError(
                    f"Aucun solde trouvé pour l'employé {demande.employe_id} "
                    f"et le type de congé {demande.type_conge_id} "
                    f"pour l'année {annee}"
                )
        else:
            # Pas le dernier niveau: passer en IN_PROGRESS
            demande.statut = StatutDemande.IN_PROGRESS.value

        await db.commit()
        await db.refresh(demande)

        return demande

    @staticmethod
    async def reject_at_level(
        demande_id: int,
        valideur_id: int,
        commentaire: Optional[str],
        db: AsyncSession
    ) -> DemandeConge:
        """
        Rejette une demande à un niveau de validation.

        Args:
            demande_id: ID de la demande
            valideur_id: ID du valideur
            commentaire: Commentaire optionnel
            db: Session de base de données

        Returns:
            La demande mise à jour

        Raises:
            ValueError: Si la demande n'existe pas ou ne peut être rejetée
        """
        # Récupérer la demande avec ses relations
        stmt = select(DemandeConge).where(DemandeConge.id == demande_id)
        result = await db.execute(stmt)
        demande = result.scalar_one_or_none()

        if not demande:
            raise ValueError(f"Demande {demande_id} non trouvée")

        # Vérifier que la demande peut être rejetée
        if demande.statut not in [
            StatutDemande.PENDING.value,
            StatutDemande.IN_PROGRESS.value
        ]:
            raise ValueError(
                f"Demande {demande_id} ne peut être rejetée "
                f"(statut: {demande.statut})"
            )

        # Créer l'entrée d'historique avec action=REJECTED
        historique = HistoriqueConge(
            demande_conge_id=demande_id,
            niveau_validation=demande.niveau_validation_actuel + 1,
            valideur_id=valideur_id,
            action=ActionHistorique.REJECTED.value,
            date_action=datetime.utcnow(),
            commentaire=commentaire
        )
        db.add(historique)

        # Restaurer le solde si déjà déduit
        # (cela arrive si la demande était APPROVED et est maintenant rejetée)
        if demande.statut == StatutDemande.APPROVED.value:
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
                solde.restant = (
                    solde.alloue - solde.utilise + solde.reporte
                )

        # Mettre le statut à REJECTED
        demande.statut = StatutDemande.REJECTED.value
        demande.date_decision_finale = datetime.utcnow()

        await db.commit()
        await db.refresh(demande)

        return demande

    @staticmethod
    async def delegate_validation(
        demande_id: int,
        valideur_id: int,
        delegue_a_id: int,
        commentaire: Optional[str],
        db: AsyncSession
    ) -> HistoriqueConge:
        """
        Délègue la validation à un autre utilisateur.

        Args:
            demande_id: ID de la demande
            valideur_id: ID du valideur qui délègue
            delegue_a_id: ID de l'utilisateur à qui déléguer
            commentaire: Commentaire optionnel
            db: Session de base de données

        Returns:
            L'entrée d'historique créée

        Raises:
            ValueError: Si la demande n'existe pas ou ne peut être déléguée
        """
        from app.user_app.models import User

        # Récupérer la demande
        stmt = select(DemandeConge).where(DemandeConge.id == demande_id)
        result = await db.execute(stmt)
        demande = result.scalar_one_or_none()

        if not demande:
            raise ValueError(f"Demande {demande_id} non trouvée")

        # Vérifier que la demande peut être déléguée
        if demande.statut not in [
            StatutDemande.PENDING.value,
            StatutDemande.IN_PROGRESS.value
        ]:
            raise ValueError(
                f"Demande {demande_id} ne peut être déléguée "
                f"(statut: {demande.statut})"
            )

        # Vérifier que le valideur peut valider au niveau actuel
        can_validate = await ValidationService.can_user_validate(
            user_id=valideur_id,
            demande_id=demande_id,
            db=db
        )

        if not can_validate:
            raise ValueError(
                f"L'utilisateur {valideur_id} ne peut pas valider "
                f"la demande {demande_id} au niveau actuel"
            )

        # Vérifier que l'utilisateur délégué existe
        stmt_user = select(User).where(User.id == delegue_a_id)
        result_user = await db.execute(stmt_user)
        delegue_user = result_user.scalar_one_or_none()

        if not delegue_user:
            raise ValueError(
                f"L'utilisateur délégué {delegue_a_id} n'existe pas"
            )

        # Créer l'entrée d'historique avec action=DELEGATED
        historique = HistoriqueConge(
            demande_conge_id=demande_id,
            niveau_validation=demande.niveau_validation_actuel + 1,
            valideur_id=valideur_id,
            action=ActionHistorique.DELEGATED.value,
            date_action=datetime.utcnow(),
            commentaire=commentaire,
            delegue_a_id=delegue_a_id
        )
        db.add(historique)

        await db.commit()
        await db.refresh(historique)

        return historique


