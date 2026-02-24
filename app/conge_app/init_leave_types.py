"""
Script to initialize default leave types

This script creates default leave types for the leave management system.

Usage:
    python -m app.conge_app.init_leave_types
"""
import asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from sqlalchemy import select
from app.core.config import settings
from app.conge_app.models import TypeConge


# Default leave types to create
DEFAULT_LEAVE_TYPES = [
    {
        "nom": "Congé Payé",
        "code": "CP",
        "nb_jours_max_par_an": 25.0,
        "report_autorise": True,
        "necessite_validation": True,
        "niveaux_validation": 2,
        "couleur": "#4CAF50",
        "description": "Congé payé annuel standard"
    },
    {
        "nom": "RTT",
        "code": "RTT",
        "nb_jours_max_par_an": 10.0,
        "report_autorise": True,
        "necessite_validation": True,
        "niveaux_validation": 1,
        "couleur": "#2196F3",
        "description": "Réduction du temps de travail"
    },
    {
        "nom": "Maladie",
        "code": "MAL",
        "nb_jours_max_par_an": 30.0,
        "report_autorise": False,
        "necessite_validation": True,
        "niveaux_validation": 1,
        "couleur": "#FF9800",
        "description": "Congé maladie"
    },
    {
        "nom": "Maternité",
        "code": "MAT",
        "nb_jours_max_par_an": 120.0,
        "report_autorise": False,
        "necessite_validation": True,
        "niveaux_validation": 2,
        "couleur": "#E91E63",
        "description": "Congé maternité"
    },
    {
        "nom": "Paternité",
        "code": "PAT",
        "nb_jours_max_par_an": 10.0,
        "report_autorise": False,
        "necessite_validation": True,
        "niveaux_validation": 1,
        "couleur": "#9C27B0",
        "description": "Congé paternité"
    },
    {
        "nom": "Sans Solde",
        "code": "SS",
        "nb_jours_max_par_an": 0.0,
        "report_autorise": False,
        "necessite_validation": True,
        "niveaux_validation": 3,
        "couleur": "#607D8B",
        "description": "Congé sans solde"
    },
]


async def init_leave_types():
    """Initialize default leave types"""
    # Create engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print(f"\n{'='*60}")
    print("🏖️  Initializing Default Leave Types")
    print(f"{'='*60}\n")

    created_count = 0
    skipped_count = 0

    async with async_session() as session:
        for leave_type_data in DEFAULT_LEAVE_TYPES:
            code = leave_type_data["code"]

            # Check if leave type already exists
            result = await session.execute(
                select(TypeConge).where(TypeConge.code == code)
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ⏭️  Skipped: {code} - {leave_type_data['nom']}")
niveaux_validation=leave_type_data["niveaux_validation"],
                couleur=leave_type_data["couleur"],
                description=leave_type_data["description"]
            )
            session.add(leave_type)
            print(f"  ✅ Created: {code} - {leave_type_data['nom']}")
            print(f"      Days/year: {leave_type_data['nb_jours_max_par_an']}")
            print(
                f"      Validation levels: "
                f"{leave_type_data['niveaux_validation']}"
            )
            print(
                f"      Carry-over: "
                f"{'Yes' if leave_type_data['report_autorise'] else 'No'}"
            )
            created_count += 1

        # Commit all leave types
        await session.commit()

    print(f"\n{'='*60}")
    print("✨ Summary:")
    print(f"  - Created: {created_count} leave types")
    print(f"  - Skipped: {skipped_count} leave types (already exist)")
    print(f"  - Total: {created_count + skipped_count} leave types")
    print(f"{'='*60}\n")


async def list_leave_types():
    """List all leave types in the database"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        result = await session.execute(
            select(TypeConge).order_by(TypeConge.code)
        )
        leave_types = result.scalars().all()

        print(f"\n{'='*60}")
        print(f"📋 All Leave Types ({len(leave_types)} total)")
        print(f"{'='*60}\n")

        for lt in leave_types:
            print(f"🔹 {lt.code} - {lt.nom}")
            print(f"   Days/year: {lt.nb_jours_max_par_an}")
            print(f"   Validation levels: {lt.niveaux_validation}")
            print(
                f"   Carry-over: "
                f"{'Yes' if lt.report_autorise else 'No'}"
            )
            print()


async def main():
    """Main function"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            await list_leave_types()
        elif command == "init":
            await init_leave_types()
        else:
            print(f"❌ Unknown command: {command}")
            print("\nUsage:")
            print("  python -m app.conge_app.init_leave_types init")
            print("  python -m app.conge_app.init_leave_types list")
    else:
        # Default: initialize leave types
        await init_leave_types()


if __name__ == "__main__":
    asyncio.run(main())
