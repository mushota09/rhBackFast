"""Fixtures pytest pour le workflow stock (SQLite in-memory).

Parallèle à ``app/paie_app/tests/conftest.py`` mais oriente le workflow vers
``code_processus='STOCK_SORTIE'`` et crée les tables ``stk_*``.
"""
from __future__ import annotations

import asyncio
from datetime import date
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.audit_app import models as _audit_models  # noqa: F401
from app.conge_app import models as _conge_models  # noqa: F401
from app.conge_app.models import (
    ActionEtapeProcessus,
    EtapeProcessus,
    StatutProcessus,
)
from app.core.database import Base
from app.paie_app import models as _paie_models  # noqa: F401
from app.reset_password_app import models as _pwd_models  # noqa: F401
from app.stock_app import models as _stock_models  # noqa: F401
from app.stock_app.constants import (
    CodeProcessusStock,
    CodeStatutStock,
    NomActionStock,
)
from app.stock_app.models import (
    Article,
    CategorieArticle,
    DemandeStock,
    DemandeStockLigne,
    UniteMesure,
)
from app.user_app import models as _user_models  # noqa: F401
from app.user_app.models import Employe, Group, Service, ServiceGroup


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


_WORKFLOW_TABLES = [
    "cg_statut_processus",
    "cg_etape_processus",
    "cg_action_etape_processus",
    "cg_demande_attribution",
    "cg_historique_demande",
]

_STOCK_TABLES = [
    "stk_categorie",
    "stk_unite_mesure",
    "stk_article",
    "stk_stock_article",
    "stk_mouvement",
    "stk_demande",
    "stk_demande_ligne",
    "stk_attribution_materiel",
]

_USER_TABLES = [
    "rh_service",
    "user_management_group",
    "rh_service_group",
    "user_management_user",
    "user_management_usergroup",
    "user_management_permission",
    "user_management_grouppermission",
    "rh_employe",
    "rh_contrat",
    "rh_document",
]


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    wanted = set(_WORKFLOW_TABLES) | set(_STOCK_TABLES) | set(_USER_TABLES)
    tables = [t for t in Base.metadata.sorted_tables if t.name in wanted]
    async with eng.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(sync_conn, tables=tables)
        )
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


def _make_employe(prenom: str, nom: str, email: str, **extra) -> Employe:
    return Employe(
        prenom=prenom,
        nom=nom,
        sexe="M",
        date_naissance=date(1980, 1, 1),
        statut_matrimonial="S",
        nationalite="FR",
        banque="N/A",
        numero_compte="0",
        niveau_etude="N/A",
        numero_inss="0",
        email_personnel=email,
        telephone_personnel="+33000000000",
        adresse_ligne1="-",
        date_embauche=date(2020, 1, 1),
        nom_contact_urgence="-",
        lien_contact_urgence="-",
        telephone_contact_urgence="+33000000000",
        **extra,
    )


@pytest_asyncio.fixture
async def stock_workflow_setup(db: AsyncSession):
    """Crée un workflow STOCK_SORTIE minimal à 2 étapes + 1 article + employés.

    - Étape 1 : Validation Responsable N+1 (is_responsable=True)
    - Étape 2 : Validation Magasinier (poste MAGASIN)

    Demande SORTIE pré-créée mais non encore soumise.
    """
    # Statuts
    statuts: dict[str, StatutProcessus] = {}
    for code in [s.value for s in CodeStatutStock]:
        st = StatutProcessus(code_statut=code)
        db.add(st)
        statuts[code] = st
    await db.flush()

    # Org
    service = Service(code="LOG", titre="Logistique", description="Stock")
    db.add(service)
    await db.flush()
    grp_mag = Group(code="MAG", name="Magasinier")
    db.add(grp_mag)
    await db.flush()
    poste_mag = ServiceGroup(service_id=service.id, group_id=grp_mag.id)
    db.add(poste_mag)
    await db.flush()

    # Étapes pour STOCK_SORTIE
    code_processus = CodeProcessusStock.SORTIE.value
    etape_resp = EtapeProcessus(
        code_processus=code_processus,
        ordre=1,
        nom_etape="Validation Responsable",
        is_responsable=True,
    )
    etape_mag = EtapeProcessus(
        code_processus=code_processus,
        ordre=2,
        nom_etape="Validation Magasinier",
        is_responsable=False,
        poste_id=poste_mag.id,
    )
    db.add_all([etape_resp, etape_mag])
    await db.flush()

    # Actions
    action_resp_appr = ActionEtapeProcessus(
        etape_id=etape_resp.id,
        nom_action=NomActionStock.APPROUVER.value,
        statut_cible_id=statuts[CodeStatutStock.EN_COURS.value].id,
        etape_suivante_id=etape_mag.id,
    )
    action_resp_rej = ActionEtapeProcessus(
        etape_id=etape_resp.id,
        nom_action=NomActionStock.REJETER.value,
        statut_cible_id=statuts[CodeStatutStock.REJETE.value].id,
        etape_suivante_id=None,
    )
    action_mag_appr = ActionEtapeProcessus(
        etape_id=etape_mag.id,
        nom_action=NomActionStock.APPROUVER.value,
        statut_cible_id=statuts[CodeStatutStock.VALIDE.value].id,
        etape_suivante_id=None,
    )
    action_mag_rej = ActionEtapeProcessus(
        etape_id=etape_mag.id,
        nom_action=NomActionStock.REJETER.value,
        statut_cible_id=statuts[CodeStatutStock.REJETE.value].id,
        etape_suivante_id=None,
    )
    db.add_all(
        [action_resp_appr, action_resp_rej, action_mag_appr, action_mag_rej]
    )
    await db.flush()

    # Employés
    demandeur = _make_employe("Dem", "Andeur", "demandeur@ex.com")
    responsable = _make_employe("Resp", "Onsable", "resp@ex.com")
    magasinier = _make_employe(
        "Mag", "Asinier", "mag@ex.com", poste_id=poste_mag.id
    )
    beneficiaire = _make_employe("Ben", "Eficiaire", "ben@ex.com")
    outsider = _make_employe("Out", "Sider", "out@ex.com")
    db.add_all([demandeur, responsable, magasinier, beneficiaire, outsider])
    await db.flush()

    # Référentiel article
    cat = CategorieArticle(code="EPI", nom="EPI")
    unite = UniteMesure(code="PCE", libelle="Pièce")
    db.add_all([cat, unite])
    await db.flush()
    article = Article(
        code="GANT-01",
        nom="Gants de protection",
        categorie_id=cat.id,
        unite_mesure_id=unite.id,
        seuil_alerte=10.0,
    )
    db.add(article)
    await db.flush()

    # Demande non soumise (1 ligne, qty 5)
    demande = DemandeStock(
        processus=code_processus,
        motif="Distribution mensuelle",
        demandeur_id=demandeur.id,
        employe_beneficiaire_id=beneficiaire.id,
    )
    db.add(demande)
    await db.flush()
    db.add(
        DemandeStockLigne(
            demande_id=demande.id, article_id=article.id, quantite=5.0
        )
    )
    await db.commit()

    return {
        "statuts": statuts,
        "etapes": {"resp": etape_resp, "mag": etape_mag},
        "actions": {
            "resp_appr": action_resp_appr,
            "resp_rej": action_resp_rej,
            "mag_appr": action_mag_appr,
            "mag_rej": action_mag_rej,
        },
        "employes": {
            "demandeur": demandeur,
            "responsable": responsable,
            "magasinier": magasinier,
            "beneficiaire": beneficiaire,
            "outsider": outsider,
        },
        "article": article,
        "demande": demande,
    }
