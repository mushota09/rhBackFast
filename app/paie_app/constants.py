"""
Constants for payroll calculations.

This module contains all the rates, caps, and scales used for payroll
calculations including INSS contributions, income tax (IRE), and family
allowances.
"""
from decimal import Decimal
from typing import Dict, List


# ============================================================================
# INSS (Institut National de Sécurité Sociale) - Social Security
# ============================================================================

# Employer contributions
INSS_PENSION_RATE = Decimal("0.06")  # 6% for pension
INSS_PENSION_CAP = Decimal("27000")  # Maximum 27,000 FC

INSS_RISK_RATE = Decimal("0.06")  # 6% for occupational risk
INSS_RISK_CAP = Decimal("2400")  # Maximum 2,400 FC

# Employee contributions
INSS_EMPLOYEE_RATE = Decimal("0.04")  # 4% for employee
INSS_EMPLOYEE_CAP = Decimal("18000")  # Maximum 18,000 FC


# ============================================================================
# IRE (Impôt sur le Revenu des Employés) - Income Tax
# ============================================================================

IRE_BRACKETS: List[Dict] = [
    {
        "min": Decimal("0"),
        "max": Decimal("150000"),
        "rate": Decimal("0.0"),  # 0% for first bracket
        "base_tax": Decimal("0")
    },
    {
        "min": Decimal("150000"),
        "max": Decimal("300000"),
        "rate": Decimal("0.2"),  # 20% for second bracket
        "base_tax": Decimal("0")
    },
    {
        "min": Decimal("300000"),
        "max": Decimal("999999999"),  # Infinity
        "rate": Decimal("0.3"),  # 30% for third bracket
        "base_tax": Decimal("30000")  # 150,000 * 0.2
    }
]


# ============================================================================
# Family Allowance Scale
# ============================================================================

FAMILY_ALLOWANCE_SCALE: Dict[int, Decimal] = {
    0: Decimal("0"),
    1: Decimal("5000"),
    2: Decimal("10000"),
    3: Decimal("15000"),
}

# Additional amount per child beyond 3
FAMILY_ALLOWANCE_ADDITIONAL = Decimal("3000")


# ============================================================================
# Deduction Types
# ============================================================================

DEDUCTION_TYPES = [
    "AVANCE_SALAIRE",  # Salary advance
    "PRET",  # Loan
    "ASSURANCE",  # Insurance
    "SYNDICAT",  # Union dues
    "AUTRE"  # Other
]


# ============================================================================
# Period Status
# ============================================================================

PERIOD_STATUS = [
    "DRAFT",  # Draft - being created
    "PROCESSING",  # Processing - calculations in progress
    "COMPLETED",  # Completed - calculations done
    "FINALIZED",  # Finalized - ready for approval
    "APPROVED",  # Approved - approved by manager
    "PAID",  # Paid - salaries have been paid
    "ARCHIVED"  # Archived - old period
]


# ============================================================================
# Alert Types and Severity
# ============================================================================

ALERT_TYPES = [
    "MISSING_CONTRACT",  # Employee has no active contract
    "NEGATIVE_SALARY",  # Calculated salary is negative
    "HIGH_DEDUCTION",  # Deductions exceed threshold
    "VALIDATION_ERROR",  # Validation error in entry
    "CALCULATION_ERROR",  # Error during calculation
    "MISSING_DATA",  # Missing required data
    "OTHER"  # Other alert type
]

ALERT_SEVERITY = [
    "LOW",  # Low severity
    "MEDIUM",  # Medium severity
    "HIGH",  # High severity
    "CRITICAL"  # Critical severity
]

ALERT_STATUS = [
    "ACTIVE",  # Active alert
    "ACKNOWLEDGED",  # Acknowledged by user
    "RESOLVED",  # Resolved
    "DISMISSED"  # Dismissed
]


# ============================================================================
# Utility Functions
# ============================================================================

def calculate_ire(base_imposable: Decimal) -> Decimal:
    """
    Calculate income tax (IRE) using progressive tax brackets.

    Args:
        base_imposable: Taxable base amount

    Returns:
        Calculated IRE amount

    Example:
        >>> calculate_ire(Decimal("100000"))
        Decimal('0')
        >>> calculate_ire(Decimal("200000"))
        Decimal('10000')  # (200000 - 150000) * 0.2
        >>> calculate_ire(Decimal("400000"))
        Decimal('60000')  # 30000 + (400000 - 300000) * 0.3
    """
    if base_imposable <= Decimal("150000"):
        return Decimal("0")
    elif base_imposable <= Decimal("300000"):
        return (base_imposable - Decimal("150000")) * Decimal("0.2")
    else:
        # 30000 (for 150k-300k) + 30% of amount above 300k
        return Decimal("30000") + (
            (base_imposable - Decimal("300000")) * Decimal("0.3")
        )


def calculate_family_allowance(nombre_enfants: int) -> Decimal:
    """
    Calculate family allowance using progressive scale.

    Args:
        nombre_enfants: Number of children

    Returns:
        Family allowance amount

    Example:
        >>> calculate_family_allowance(0)
        Decimal('0')
        >>> calculate_family_allowance(1)
        Decimal('5000')
        >>> calculate_family_allowance(3)
        Decimal('15000')
        >>> calculate_family_allowance(5)
        Decimal('21000')  # 15000 + (2 * 3000)
    """
    if nombre_enfants <= 0:
        return Decimal("0")

    # Use scale for 0-3 children
    if nombre_enfants in FAMILY_ALLOWANCE_SCALE:
        return FAMILY_ALLOWANCE_SCALE[nombre_enfants]

    # For more than 3 children, add additional amount per child
    base_amount = FAMILY_ALLOWANCE_SCALE[3]
    additional_children = nombre_enfants - 3
    additional_amount = FAMILY_ALLOWANCE_ADDITIONAL * additional_children

    return base_amount + additional_amount


def calculate_inss_employer(gross_salary: Decimal) -> Dict[str, Decimal]:
    """
    Calculate employer INSS contributions (pension + risk).

    Args:
        gross_salary: Gross salary amount

    Returns:
        Dict with pension, risk, and total contributions

    Example:
        >>> calculate_inss_employer(Decimal("100000"))
        {'pension': Decimal('6000'), 'risk': Decimal('2400'), 'total': Decimal('8400')}
    """
    pension = min(gross_salary * INSS_PENSION_RATE, INSS_PENSION_CAP)
    risk = min(gross_salary * INSS_RISK_RATE, INSS_RISK_CAP)

    return {
        "pension": pension,
        "risk": risk,
        "total": pension + risk
    }


def calculate_inss_employee(gross_salary: Decimal) -> Decimal:
    """
    Calculate employee INSS contribution.

    Args:
        gross_salary: Gross salary amount

    Returns:
        Employee INSS contribution amount

    Example:
        >>> calculate_inss_employee(Decimal("100000"))
        Decimal('4000')  # 100000 * 0.04
        >>> calculate_inss_employee(Decimal("500000"))
        Decimal('18000')  # Capped at 18000
    """
    return min(gross_salary * INSS_EMPLOYEE_RATE, INSS_EMPLOYEE_CAP)


def validate_period_status_transition(
    current_status: str,
    new_status: str
) -> bool:
    """
    Validate if a period status transition is allowed.

    Args:
        current_status: Current period status
        new_status: Desired new status

    Returns:
        True if transition is allowed, False otherwise

    Allowed transitions:
        DRAFT -> PROCESSING
        PROCESSING -> COMPLETED
        COMPLETED -> FINALIZED
        FINALIZED -> APPROVED
        APPROVED -> PAID
        PAID -> ARCHIVED
    """
    allowed_transitions = {
        "DRAFT": ["PROCESSING"],
        "PROCESSING": ["COMPLETED", "DRAFT"],
        "COMPLETED": ["FINALIZED", "PROCESSING"],
        "FINALIZED": ["APPROVED", "COMPLETED"],
        "APPROVED": ["PAID"],
        "PAID": ["ARCHIVED"],
        "ARCHIVED": []  # No transitions from archived
    }

    allowed = allowed_transitions.get(current_status, [])
    return new_status in allowed
