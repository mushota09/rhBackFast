"""Service for SoldeConge management"""
from typing import Optional, Tuple, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.conge_app.models import SoldeConge, TypeConge
from app.conge_app.schemas import SoldeCongeCreate, SoldeCongeUpdate
from app.core.query_utils import (
    apply_ordering, apply_expansion, parse_expand_param
)
from app.user_app.models import Employe


class SoldeCongeService:
    """Service for managing SoldeConge operations"""

    @staticmethod
    def _calculate_restant(alloue: float, utilise: float, reporte: float) -> float:
        """Calculate remaining balance: alloue - utilise + reporte"""
        return alloue - utilise + reporte

    @staticmethod
    async def create_solde(
        solde_data: SoldeCongeCreate,
        db: AsyncSession
    ) -> SoldeConge:
        """
        Create a new SoldeConge with automatic restant calculation.

        Args:
            solde_data: SoldeConge creation data
            db: Database session

        Returns:
            Created SoldeConge instance

        Raises:
            HTTPException: If employe or type_conge doesn't exist,
                       or if solde already exists for this combination
        """
        # Validate employe exists
        employe_query = select(Employe).where(
            Employe.id == solde_data.employe_id
        )
        result = await db.execute(employe_query)
        employe = result.scalar_one_or_none()

        if not employe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employé avec ID {solde_data.employe_id} n'existe pas"
            )

        # Validate type_conge exists
        type_query = select(TypeConge).where(
            TypeConge.id == solde_data.type_conge_id
        )
        result = await db.execute(type_query)
        type_conge = result.scalar_one_or_none()

        if not type_conge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Type de congé avec ID {solde_data.type_conge_id} n'existe pas"
            )

        # Check if solde already exists for this combination
        existing_query = select(SoldeConge).where(
            and_(
                SoldeConge.employe_id == solde_data.employe_id,
                SoldeConge.type_conge_id == solde_data.type_conge_id,
                SoldeConge.annee == solde_data.annee
            )
        )
        result = await db.execute(existing_query)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Un solde existe déjà pour l'employé {solde_data.employe_id}, "
                    f"type {solde_data.type_conge_id}, année {solde_data.annee}"
                )
            )

        # Create solde with calculated restant
        solde_dict = solde_data.model_dump()
        solde_dict['utilise'] = 0.0  # Initial utilise is 0
        solde_dict['restant'] = SoldeCongeService._calculate_restant(
            solde_dict['alloue'],
            0.0,
            solde_dict['reporte']
        )

        new_solde = SoldeConge(**solde_dict)
        db.add(new_solde)
        await db.commit()
        await db.refresh(new_solde)

        return new_solde

    @staticmethod
    async def update_solde(
        solde_id: int,
        solde_data: SoldeCongeUpdate,
        db: AsyncSession
    ) -> SoldeConge:
        """
        Update a SoldeConge with automatic restant recalculation.

        Args:
            solde_id: ID of the solde to update
            solde_data: Update data
            db: Database session

        Returns:
            Updated SoldeConge instance

        Raises:
            HTTPException: If solde not found
        """
        query = select(SoldeConge).where(SoldeConge.id == solde_id)
        result = await db.execute(query)
        solde = result.scalar_one_or_none()

        if not solde:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solde de congé non trouvé"
            )

        # Update fields
        update_data = solde_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(solde, field, value)

        # Recalculate restant
        solde.restant = SoldeCongeService._calculate_restant(
            solde.alloue,
            solde.utilise,
            solde.reporte
        )

        await db.commit()
        await db.refresh(solde)

        return solde

    @staticmethod
    async def list_soldes(
        filters: dict,
        expand: Optional[str],
        skip: int,
        limit: Optional[int],
        no_pagination: bool,
        search: Optional[str],
        ordering: Optional[str],
        db: AsyncSession
    ) -> Tuple[List[SoldeConge], int]:
        """
        List SoldeConge with filters, pagination, and expand support.

        Args:
            filters: Dictionary of filters (employe_id, type_conge_id, annee)
            expand: Comma-separated list of relations to expand
            skip: Number of records to skip
            limit: Maximum number of records to return
            no_pagination: If True, return all results
            search: Search term (not used for SoldeConge)
            ordering: Field to order by
            db: Database session

        Returns:
            Tuple of (list of SoldeConge, total count)
        """
        query = select(SoldeConge)

        # Apply filters
        if 'employe_id' in filters:
            query = query.where(SoldeConge.employe_id == filters['employe_id'])
        if 'type_conge_id' in filters:
            query = query.where(
                SoldeConge.type_conge_id == filters['type_conge_id']
            )
        if 'annee' in filters:
            query = query.where(SoldeConge.annee == filters['annee'])

        # Apply ordering
        if ordering:
            query = apply_ordering(query, SoldeConge, ordering)
        else:
            query = query.order_by(
                SoldeConge.annee.desc(),
                SoldeConge.employe_id.asc()
            )

        # Apply expansion
        expand_fields = parse_expand_param(expand)
        if expand_fields:
            query = apply_expansion(query, SoldeConge, expand_fields)

        # Count total
        count_query = select(func.count()).select_from(SoldeConge)
        if 'employe_id' in filters:
            count_query = count_query.where(
                SoldeConge.employe_id == filters['employe_id']
            )
        if 'type_conge_id' in filters:
            count_query = count_query.where(
                SoldeConge.type_conge_id == filters['type_conge_id']
            )
        if 'annee' in filters:
            count_query = count_query.where(SoldeConge.annee == filters['annee'])

        result = await db.execute(count_query)
        total = result.scalar()

        # Apply pagination
        if not no_pagination and limit is not None:
            query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        soldes = result.scalars().all()

        return list(soldes), total

    @staticmethod
    async def bulk_create_soldes(
        annee: int,
        type_conge_id: int,
        alloue: float,
        db: AsyncSession
    ) -> List[SoldeConge]:
        """
        Create soldes for all employees for a given year and leave type.

        Args:
            annee: Year for the soldes
            type_conge_id: Leave type ID
            alloue: Number of days to allocate
            db: Database session

        Returns:
            List of created SoldeConge instances

        Raises:
            HTTPException: If type_conge doesn't exist
        """
        # Validate type_conge exists
        type_query = select(TypeConge).where(TypeConge.id == type_conge_id)
        result = await db.execute(type_query)
        type_conge = result.scalar_one_or_none()

        if not type_conge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Type de congé avec ID {type_conge_id} n'existe pas"
            )

        # Get all employees
        employes_query = select(Employe)
        result = await db.execute(employes_query)
        employes = result.scalars().all()

        created_soldes = []
        skipped_count = 0

        for employe in employes:
            # Check if solde already exists
            existing_query = select(SoldeConge).where(
                and_(
                    SoldeConge.employe_id == employe.id,
                    SoldeConge.type_conge_id == type_conge_id,
                    SoldeConge.annee == annee
                )
            )
            result = await db.execute(existing_query)
            existing = result.scalar_one_or_none()

            if existing:
                skipped_count += 1
                continue

            # Create solde
            new_solde = SoldeConge(
                employe_id=employe.id,
                type_conge_id=type_conge_id,
                annee=annee,
                alloue=alloue,
                utilise=0.0,
                restant=alloue,  # restant = alloue - 0 + 0
                reporte=0.0
            )
            db.add(new_solde)
            created_soldes.append(new_solde)

        await db.commit()

        # Refresh all created soldes
        for solde in created_soldes:
            await db.refresh(solde)

        return created_soldes
