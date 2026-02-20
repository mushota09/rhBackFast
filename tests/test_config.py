"""
Property-based tests for configuration management
"""
import os
import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import decimals

from app.core.config import PayrollSettings, validate_configuration


class TestConfigurationAccessibility:
    """Property 4: Payroll Configuration Accessibility"""

    def test_payroll_constants_accessible_from_config(self):
        """
        Feature: rhback-migration, Property 4: Payroll Configuration Accessibility
        For any payroll constant, the value should be accessible from config.py
        """
        payroll_config = PayrollSettings()

        # Verify all INSS constants are accessible
        assert hasattr(payroll_config, 'INSS_PENSION_RATE')
        assert hasattr(payroll_config, 'INSS_PENSION_CAP')
        assert hasattr(payroll_config, 'INSS_RISK_RATE')
        assert hasattr(payroll_config, 'INSS_RISK_CAP')
        assert hasattr(payroll_config, 'INSS_EMPLOYEE_RATE')
        assert hasattr(payroll_config, 'INSS_EMPLOYEE_CAP')

        # Verify IRE brackets are accessible
        assert hasattr(payroll_config, 'IRE_BRACKETS')
        assert isinstance(payroll_config.IRE_BRACKETS, list)
        assert len(payroll_config.IRE_BRACKETS) > 0

        # Verify family allowance scale is accessible
        assert hasattr(payroll_config, 'FAMILY_ALLOWANCE_SCALE')
        assert isinstance(payroll_config.FAMILY_ALLOWANCE_SCALE, list)
        assert len(payroll_config.FAMILY_ALLOWANCE_SCALE) > 0

    @given(rate_value=decimals(min_value=0, max_value=1, places=4))
    @settings(max_examples=100)
    def test_environment_variable_override(self, rate_value: Decimal):
        """
        Feature: rhback-migration, Property 4: Payroll Configuration Accessibility
        Test that environment variables can override configuration values
        """
        env_var = "PAYROLL__INSS_PENSION_RATE"
        original_value = os.environ.get(env_var)

        try:
            os.environ[env_var] = str(rate_value)
            payroll_config = PayrollSettings()
            assert payroll_config.INSS_PENSION_RATE == rate_value
        finally:
            if original_value is not None:
                os.environ[env_var] = original_value
            else:
                os.environ.pop(env_var, None)


class TestConfigurationValidation:
    """Property 15: Configuration Validation at Startup"""

    def test_valid_configuration_passes_validation(self):
        """
        Feature: rhback-migration, Property 15: Configuration Validation at Startup
        Test that valid configuration passes validation without errors
        """
        validate_configuration()

    @given(invalid_rate=st.one_of(
        decimals(min_value=-1, max_value=-0.01, places=4),
        decimals(min_value=1.01, max_value=10, places=4)
    ))
    @settings(max_examples=100)
    def test_invalid_rates_fail_validation(self, invalid_rate: Decimal):
        """
        Feature: rhback-migration, Property 15: Configuration Validation at Startup
        Test that invalid rates fail validation
        """
        env_var = "PAYROLL__INSS_PENSION_RATE"
        original_value = os.environ.get(env_var)

        try:
            os.environ[env_var] = str(invalid_rate)
            with pytest.raises(ValueError, match="Rates must be between 0 and 1"):
                PayrollSettings()
        finally:
            if original_value is not None:
                os.environ[env_var] = original_value
            else:
                os.environ.pop(env_var, None)
