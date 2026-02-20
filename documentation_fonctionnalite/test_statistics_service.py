"""Test script for StatisticsService"""
import asyncio
from app.paie_app.services.statistics_service import StatisticsService


async def test_service_instantiation():
    """Test that StatisticsService can be instantiated"""
    # Mock db session (we're just testing instantiation)
    class MockDB:
        pass

    db = MockDB()
    service = StatisticsService(db)

    # Check that all methods exist
    methods = [
        'get_period_summary',
        'get_annual_summary',
        'get_employee_payroll_history',
        'get_deductions_summary',
        'get_alerts_summary',
        'get_comparative_analysis',
        'get_top_earners',
        'get_dashboard_summary',
    ]

    for method in methods:
        assert hasattr(service, method), f"Method {method} not found"
        print(f"✓ Method {method} exists")

    print("\n✅ All StatisticsService methods are available")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_service_instantiation())
    if result:
        print("\n🎉 StatisticsService test passed!")
