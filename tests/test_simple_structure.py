"""Simple structure tests to verify modules work"""


def test_user_app_imports():
    """Test user_app can be imported"""
    from app.user_app import models
    assert hasattr(models, 'User')
    assert hasattr(models, 'Employe')
    assert hasattr(models, 'Service')
    print("\n✅ user_app imports OK")


def test_audit_app_imports():
    """Test audit_app can be imported"""
    from app.audit_app import models
    assert hasattr(models, 'AuditLog')
    print("✅ audit_app imports OK")


def test_paie_app_imports():
    """Test paie_app can be imported"""
    from app.paie_app import models
    assert hasattr(models, 'PeriodePaie')
    assert hasattr(models, 'EntreePaie')
    assert hasattr(models, 'RetenueEmploye')
    assert hasattr(models, 'Alert')
    print("✅ paie_app imports OK")


def test_paie_services():
    """Test paie services can be imported"""
    from app.paie_app.services import (
        SalaryCalculatorService,
        PeriodProcessorService,
        DeductionManagerService,
        PayslipGeneratorService,
        ExportService,
        StatisticsService
    )
    assert SalaryCalculatorService is not None
    assert PeriodProcessorService is not None
    assert DeductionManagerService is not None
    assert PayslipGeneratorService is not None
    assert ExportService is not None
    assert StatisticsService is not None
    print("✅ paie_app services OK")


def test_paie_constants():
    """Test paie constants"""
    from app.paie_app.constants import (
        INSS_PENSION_RATE,
        INSS_EMPLOYEE_RATE,
        IRE_BRACKETS
    )
    from decimal import Decimal

    assert INSS_PENSION_RATE == Decimal("0.06")
    assert INSS_EMPLOYEE_RATE == Decimal("0.04")
    assert len(IRE_BRACKETS) >= 1
    print("✅ paie_app constants OK")


def test_paie_routes():
    """Test paie routes"""
    from app.paie_app.routes import (
        alert_router,
        retenue_router,
        periode_router,
        entree_router,
        payroll_router,
        statistics_router
    )

    assert alert_router.prefix == "/alerts"
    assert retenue_router.prefix == "/retenues"
    assert periode_router.prefix == "/periodes"
    assert entree_router.prefix == "/entrees"
    assert payroll_router.prefix == "/payroll"
    assert statistics_router.prefix == "/statistics"
    print("✅ paie_app routes OK")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
