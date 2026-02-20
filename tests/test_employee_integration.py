"""Integration tests for employee management with PostgreSQL database"""
import pytest
import pytest_asyncio
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.user_app.models import (
    Employe, User, Group, UserGroup, Service, ServiceGroup
)
from app.user_app.services import EmployeeService
from app.user_app.schemas import EmployeCreate, EmployeCreateWithUser


@pytest_asyncio.fixture
async def test_service(db_session: AsyncSession):
    """Create a test service"""
    service = Service(
        code="IT",
        titre="Information Technology",
        description="IT Department",
        is_active=True
    )
    db_session.add(service)
    await db_session.flush()
    await db_session.refresh(service)
    return service


@pytest_asyncio.fixture
async def test_group(db_session: AsyncSession):
    """Create a test group"""
    group = Group(
        code="DEV",
        name="Developers",
        description="Development Team",
        is_active=True
    )
    db_session.add(group)
    await db_session.flush()
    await db_session.refresh(group)
    return group


@pytest_asyncio.fixture
async def test_service_group(db_session: AsyncSession, test_service, test_group):
    """Create a test service group"""
    service_group = ServiceGroup(
        service_id=test_service.id,
        group_id=test_group.id
    )
    db_session.add(service_group)
    await db_session.flush()
    await db_session.refresh(service_group)
    return service_group


@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession):
    """Create a test admin user"""
    from app.core.security import get_password_hash

    admin = User(
        email="admin@test.com",
        nom="Admin",
        prenom="Test",
        password=get_password_hash("admin123"),
        is_active=True,
        is_staff=True,
        is_superuser=True
    )
    db_session.add(admin)
    await db_session.flush()
    await db_session.refresh(admin)
    return admin



class TestEmployeeCreationIntegration:
    """Integration tests for employee creation with PostgreSQL database"""

    @pytest.mark.asyncio
    async def test_create_basic_employee(self, db_session: AsyncSession):
        """Test creating a basic employee without user account"""
        employee_data = EmployeCreate(
            prenom="Jean",
            nom="Dupont",
            postnom="Marie",
            date_naissance=date(1990, 5, 15),
            sexe="M",
            statut_matrimonial="M",
            nationalite="Congolaise",
            banque="BCDC",
            numero_compte="123456789",
            niveau_etude="Licence",
            numero_inss="INSS123456",
            email_personnel="jean.dupont@email.com",
            email_professionnel="jean.dupont@company.com",
            telephone_personnel="+243999999999",
            telephone_professionnel="+243888888888",
            adresse_ligne1="123 Avenue de la Paix",
            adresse_ligne2="Appartement 4B",
            ville="Kinshasa",
            province="Kinshasa",
            code_postal="12345",
            pays="RDC",
            matricule="EMP001",
            date_embauche=date(2024, 1, 1),
            statut_emploi="ACTIVE",
            nombre_enfants=2,
            nom_conjoint="Marie Dupont",
            biographie="Employé expérimenté",
            nom_contact_urgence="Pierre Dupont",
            lien_contact_urgence="Frère",
            telephone_contact_urgence="+243777777777"
        )

        employee = await EmployeeService.create_employee(db_session, employee_data)
        await db_session.flush()
        await db_session.refresh(employee)

        assert employee.id is not None
        assert employee.prenom == "Jean"
        assert employee.nom == "Dupont"
        assert employee.full_name == "Dupont Marie Jean"

        print(f"\n✓ Employee created: {employee.full_name} (ID: {employee.id})")

    @pytest.mark.asyncio
    async def test_create_employee_with_user_account(
        self,
        db_session: AsyncSession,
        test_admin_user
    ):
        """Test creating employee with user account (rhBack logic)"""
        employee_data = EmployeCreateWithUser(
            prenom="Bob",
            nom="Johnson",
            date_naissance=date(1988, 7, 10),
            sexe="M",
            statut_matrimonial="M",
            nationalite="Congolaise",
            banque="EQUITY",
            numero_compte="555666777",
            niveau_etude="Licence",
            numero_inss="INSS345678",
            email_personnel="bob.johnson@email.com",
            email_professionnel="bob.johnson@company.com",
            telephone_personnel="+243444444444",
            adresse_ligne1="789 Rue de la Liberté",
            ville="Lubumbashi",
            date_embauche=date(2024, 3, 1),
            nom_contact_urgence="Jane Johnson",
            lien_contact_urgence="Épouse",
            telephone_contact_urgence="+243333333333",
            password="secure123"
        )

        result = await EmployeeService.create_employee_with_user(
            db_session,
            employee_data,
            created_by=test_admin_user
        )

        employee = result["employee"]
        user = result["user"]

        assert employee.id is not None
        assert user is not None
        assert user.email == "bob.johnson@company.com"
        assert user.employe_id == employee.id

        print(f"\n✓ Employee with user created: {employee.full_name}")
        print(f"  User: {user.email}")

    @pytest.mark.asyncio
    async def test_create_employee_with_user_and_group(
        self,
        db_session: AsyncSession,
        test_group,
        test_admin_user
    ):
        """Test creating employee with user account and group assignment"""
        employee_data = EmployeCreateWithUser(
            prenom="Carol",
            nom="Williams",
            date_naissance=date(1995, 11, 25),
            sexe="F",
            statut_matrimonial="S",
            nationalite="Congolaise",
            banque="TMB",
            numero_compte="111222333",
            niveau_etude="Master",
            numero_inss="INSS901234",
            email_personnel="carol.williams@email.com",
            email_professionnel="carol.williams@company.com",
            telephone_personnel="+243222222222",
            adresse_ligne1="321 Avenue Mobutu",
            ville="Goma",
            date_embauche=date(2024, 4, 1),
            nom_contact_urgence="David Williams",
            lien_contact_urgence="Père",
            telephone_contact_urgence="+243111111111",
            password="password123",
            group_id=test_group.id
        )

        result = await EmployeeService.create_employee_with_user(
            db_session,
            employee_data,
            created_by=test_admin_user
        )

        assert result["group_assigned"] is True

        result_db = await db_session.execute(
            select(UserGroup).where(
                UserGroup.user_id == result["user"].id,
                UserGroup.group_id == test_group.id
            )
        )
        user_group = result_db.scalar_one_or_none()
        assert user_group is not None
        assert user_group.is_active is True

        print(f"\n✓ Employee with user and group created: {result['employee'].full_name}")
        print(f"  Group: {test_group.code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
