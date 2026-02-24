"""
Script to initialize holidays for supported countries

This script loads holidays for CD, FR, and BE for years 2024-2026.

Usage:
    python -m app.conge_app.init_holidays
"""
import asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from sqlalchemy import select
from app.core.config import settings
from app.conge_app.services.holiday_service import HolidayService
from app.conge_app.models import JourFerie


# Countries and years to load
COUNTRIES = ["CD", "FR", "BE"]
YEARS = [2024, 2025, 2026]


async def init_holidays():
    """Initialize holidays for all countries and years"""
    # Create engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print(f"\n{'='*60}")
    print("🎉 Initializing Holidays")
    print(f"{'='*60}\n")

    total_loaded = 0
    results = {}

    async with async_session() as session:
        for country in COUNTRIES:
            results[country] = {}
            print(f"\n🌍 Loading holidays for {country}")

            for year in YEARS:
                try:
                    # Count existing holidays before loading
                    stmt = select(JourFerie).where(
                        JourFerie.pays_code == country,
                        JourFerie.annee == year
                    )
                    result = await session.execute(stmt)
                    before_count = len(result.scalars().all())

                    # Load holidays using HolidayService
                    await HolidayService.load_holidays_for_country(
                        country, year, session
                    )

                    # Count holidays after loading
                    result = await session.execute(stmt)
                    after_count = len(result.scalars().all())

                    loaded = after_count - before_count
                    results[country][year] = {
                        "loaded": loaded,
                        "total": after_count
                    }
                    total_loaded += loaded

                    msg = (
                        f"  ✅ {year}: Loaded {loaded} new holidays "
                        f"(total: {after_count})"
                    )
                    print(msg)

                except ValueError as e:
                    print(f"  ❌ {year}: Error - {e}")
                    results[country][year] = {"error": str(e)}
                except Exception as e:
                    print(f"  ❌ {year}: Unexpected error - {e}")
                    results[country][year] = {"error": str(e)}

    print(f"\n{'='*60}")
    print("✨ Summary:")
    print(f"  Total new holidays loaded: {total_loaded}")
    print(f"\n  Details by country:")
    for country, years_data in results.items():
        print(f"\n  🌍 {country}:")
        for year, data in years_data.items():
            if "error" in data:
                print(f"    {year}: ❌ {data['error']}")
            else:
                msg = (
                    f"    {year}: {data['loaded']} new "
                    f"(total: {data['total']})"
                )
                print(msg)
    print(f"\n{'='*60}\n")


async def list_holidays():
    """List all holidays in the database"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        result = await session.execute(
            select(JourFerie).order_by(
                JourFerie.pays_code,
                JourFerie.annee,
                JourFerie.date_ferie
            )
        )
        holidays_list = result.scalars().all()

        print(f"\n{'='*60}")
        print(f"📋 All Holidays ({len(holidays_list)} total)")
        print(f"{'='*60}\n")

        current_country = None
        current_year = None

        for holiday in holidays_list:
            if holiday.pays_code != current_country:
                current_country = holiday.pays_code
                print(f"\n🌍 {current_country}")

            if holiday.annee != current_year:
                current_year = holiday.annee
                print(f"\n  📅 {current_year}")

            type_indicator = ""
            if holiday.type_date == "ESTIMATED":
                type_indicator = " (estimated)"
            elif holiday.type_date == "OBSERVED":
                type_indicator = " (observed)"

            custom = " [custom]" if holiday.est_personnalise else ""

            msg = (
                f"    {holiday.date_ferie}: {holiday.nom}"
                f"{type_indicator}{custom}"
            )
            print(msg)


async def count_holidays():
    """Count holidays by country and year"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print(f"\n{'='*60}")
        print("📊 Holiday Statistics")
        print(f"{'='*60}\n")

        for country in COUNTRIES:
            print(f"\n🌍 {country}:")
            for year in YEARS:
                stmt = select(JourFerie).where(
                    JourFerie.pays_code == country,
                    JourFerie.annee == year
                )
                result = await session.execute(stmt)
                count = len(result.scalars().all())
                print(f"  {year}: {count} holidays")


async def main():
    """Main function"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            await list_holidays()
        elif command == "count":
            await count_holidays()
        elif command == "init":
            await init_holidays()
        else:
            print(f"❌ Unknown command: {command}")
            print("\nUsage:")
            print("  python -m app.conge_app.init_holidays init")
            print("  python -m app.conge_app.init_holidays list")
            print("  python -m app.conge_app.init_holidays count")
    else:
        # Default: initialize holidays
        await init_holidays()


if __name__ == "__main__":
    asyncio.run(main())
