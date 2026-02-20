"""Test modification history service"""
import asyncio
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.paie_app.models import EntreePaie, RetenueEmploye
from app.paie_app.services.modification_history_service import (
    ModificationHistoryService
)
from app.user_app.models import User


async def test_modification_history():
    """Test the modification history service"""
    print("🧪 Testing Modification History Service...")

    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        try:
            # Test 1: Extract model values
            print("\n✅ Test 1: Extract model values")

            # Create a mock entree for testing
            test_entree = EntreePaie(
                id=999999,
                employe_id=1,
                periode_paie_id=1,
                salaire_base=Decimal("1500000.00"),
                salaire_brut=Decimal("1800000.00"),
                salaire_net=Decimal("1400000.00"),
                indemnite_logement=Decimal("300000.00"),
                indemnite_deplacement=Decimal("0.00"),
                indemnite_fonction=Decimal("0.00"),
                allocation_familiale=Decimal("0.00"),
                autres_avantages=Decimal("0.00"),
                total_charge_salariale=Decimal("400000.00"),
                base_imposable=Decimal("1500000.00")
            )

            values = ModificationHistoryService.extract_model_values(
                test_entree
            )
            print(f"   Extracted {len(values)} fields")
            assert 'salaire_base' in values
            assert values['salaire_base'] == 1500000.0
            print("   ✓ Values extracted correctly")

            # Test 2: Compute changes
            print("\n✅ Test 2: Compute changes")

            old_values = {
                'salaire_base': 1500000.0,
                'salaire_brut': 1800000.0,
                'salaire_net': 1400000.0
            }

            new_values = {
                'salaire_base': 1600000.0,  # Changed
                'salaire_brut': 1900000.0,  # Changed
                'salaire_net': 1400000.0    # Unchanged
            }

            changes = ModificationHistoryService._compute_changes(
                old_values, new_values
            )

            print(f"   Detected {len(changes)} changes")
            assert 'salaire_base' in changes
            assert 'salaire_brut' in changes
            assert 'salaire_net' not in changes  # Unchanged
            assert changes['salaire_base']['old'] == 1500000.0
            assert changes['salaire_base']['new'] == 1600000.0
            print("   ✓ Changes computed correctly")

            # Test 3: Test retenue model values
            print("\n✅ Test 3: Extract retenue values")

            test_retenue = RetenueEmploye(
                id=999999,
                employe_id=1,
                type_retenue="PRET",
                description="Test deduction",
                montant_mensuel=Decimal("50000.00"),
                montant_total=Decimal("500000.00"),
                montant_deja_deduit=Decimal("100000.00"),
                date_debut=date(2024, 1, 1),
                est_active=True,
                est_recurrente=False
            )

            retenue_values = ModificationHistoryService.extract_model_values(
                test_retenue
            )
            print(f"   Extracted {len(retenue_values)} fields")
            assert 'type_retenue' in retenue_values
            assert 'montant_mensuel' in retenue_values
            print("   ✓ Retenue values extracted correctly")

            print("\n✅ All tests passed!")
            print("\n📝 Note: Integration tests require database access")
            print("   Run the application to test full functionality")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_modification_history())

