"""Seed script producing realistic mock data for user_app, conge_app, paie_app.

Idempotent: safe to run multiple times — existing rows (matched by natural
keys such as email, matricule, (annee,mois), (employe,type,annee)...) are
reused rather than duplicated.

Usage::

    uv run python -m scripts.seed_mock_data            # insert / upsert mock data
    uv run python -m scripts.seed_mock_data --reset    # delete mock rows first
    uv run python -m scripts.seed_mock_data --quiet    # minimal output

The default password for all generated user accounts is ``rapha12345678``.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conge_app.constants import CodeProcessus, CodeStatut
from app.conge_app.init_data import init_conge_defaults
from app.conge_app.models import (
    DemandeConge,
    EtapeProcessus,
    SoldeConge,
    StatutProcessus,
    TypeConge,
)
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.paie_app.constants import (
    AlertSeverity,
    AlertStatus,
    AlertType,
    DeductionType,
    PeriodeStatutTexte,
)
from app.paie_app.init_data import init_paie_workflow_defaults
from app.paie_app.models import Alert, EntreePaie, PeriodePaie, RetenueEmploye
from app.user_app.constants import (
    Sexe,
    StatutEmploi,
    StatutMatrimonial,
    TypeContrat,
)
from app.user_app.models import (
    Contrat,
    Employe,
    Group,
    Service,
    ServiceGroup,
    User,
    UserGroup,
)

DEFAULT_PASSWORD = "rapha12345678"


# ---------------------------------------------------------------------------
# Reference data (services, groups, postes)
# ---------------------------------------------------------------------------

SERVICES: list[dict[str, str]] = [
    {"code": "DIR", "titre": "Direction Générale"},
    {"code": "RH", "titre": "Ressources Humaines"},
    {"code": "IT", "titre": "Systèmes d'Information"},
    {"code": "FIN", "titre": "Finance & Comptabilité"},
    {"code": "OPS", "titre": "Opérations"},
]

GROUPS: list[dict[str, str]] = [
    {"code": "DIRECTION", "name": "Direction"},
    {"code": "MANAGER", "name": "Chef de service"},
    {"code": "EMPLOYEE", "name": "Employé"},
    {"code": "ADMIN_RH", "name": "Administrateur RH"},
]

# (service_code, group_code) pairs that form the "postes" assignable to an
# employee. The first item becomes the primary poste for the service lead.
POSTES: list[tuple[str, str]] = [
    ("DIR", "DIRECTION"),
    ("RH", "ADMIN_RH"),
    ("RH", "MANAGER"),
    ("IT", "MANAGER"),
    ("IT", "EMPLOYEE"),
    ("FIN", "MANAGER"),
    ("FIN", "EMPLOYEE"),
    ("OPS", "EMPLOYEE"),
]


# ---------------------------------------------------------------------------
# Employees + user accounts (emails hard-coded per user request)
# ---------------------------------------------------------------------------

# Email list: first 4 are explicitly provided by the user, the rest are
# imagined. Password is DEFAULT_PASSWORD for every account.
EMPLOYEES: list[dict[str, Any]] = [
    {
        "prenom": "Raphaël",
        "nom": "Mushota",
        "matricule": "EMP-001",
        "email_personnel": "mushota09@gmail.com",
        "sexe": Sexe.MASCULIN.value,
        "statut_matrimonial": StatutMatrimonial.MARIE.value,
        "date_naissance": date(1988, 4, 12),
        "date_embauche": date(2018, 3, 1),
        "nationalite": "Congolaise",
        "poste": ("DIR", "DIRECTION"),
        "is_superuser": True,
        "is_staff": True,
        "salaire_base": Decimal("3500000"),
        "type_contrat": TypeContrat.CDI.value,
        "nombre_enfants": 2,
        "nom_conjoint": "Aimée Mushota",
    },
    {
        "prenom": "Raphaël",
        "nom": "Mushotaraphael",
        "matricule": "EMP-002",
        "email_personnel": "mushotaraphael09@gmail.com",
        "sexe": Sexe.MASCULIN.value,
        "statut_matrimonial": StatutMatrimonial.CELIBATAIRE.value,
        "date_naissance": date(1992, 7, 22),
        "date_embauche": date(2020, 9, 15),
        "nationalite": "Congolaise",
        "poste": ("RH", "ADMIN_RH"),
        "is_staff": True,
        "salaire_base": Decimal("2200000"),
        "type_contrat": TypeContrat.CDI.value,
    },
    {
        "prenom": "Raphaël",
        "nom": "Mushotaraphael",
        "postnom": "07",
        "matricule": "EMP-003",
        "email_personnel": "mushotaraphael07@gmail.com",
        "sexe": Sexe.MASCULIN.value,
        "statut_matrimonial": StatutMatrimonial.CELIBATAIRE.value,
        "date_naissance": date(1995, 1, 30),
        "date_embauche": date(2022, 2, 1),
        "nationalite": "Congolaise",
        "poste": ("RH", "MANAGER"),
        "salaire_base": Decimal("1800000"),
        "type_contrat": TypeContrat.CDI.value,
    },
    {
        "prenom": "Chris",
        "nom": "Cedrick",
        "matricule": "EMP-004",
        "email_personnel": "chriscedrick4@gmail.com",
        "sexe": Sexe.MASCULIN.value,
        "statut_matrimonial": StatutMatrimonial.MARIE.value,
        "date_naissance": date(1990, 11, 5),
        "date_embauche": date(2019, 6, 15),
        "nationalite": "Congolaise",
        "poste": ("IT", "MANAGER"),
        "is_staff": True,
        "salaire_base": Decimal("2500000"),
        "type_contrat": TypeContrat.CDI.value,
        "nombre_enfants": 1,
        "nom_conjoint": "Sarah Cedrick",
    },
    {
        "prenom": "Grace",
        "nom": "Kalombo",
        "matricule": "EMP-005",
        "email_personnel": "grace.kalombo@example.com",
        "sexe": Sexe.FEMININ.value,
        "statut_matrimonial": StatutMatrimonial.CELIBATAIRE.value,
        "date_naissance": date(1996, 3, 18),
        "date_embauche": date(2023, 1, 10),
        "nationalite": "Congolaise",
        "poste": ("IT", "EMPLOYEE"),
        "salaire_base": Decimal("1400000"),
        "type_contrat": TypeContrat.CDI.value,
    },
    {
        "prenom": "David",
        "nom": "Ilunga",
        "matricule": "EMP-006",
        "email_personnel": "david.ilunga@example.com",
        "sexe": Sexe.MASCULIN.value,
        "statut_matrimonial": StatutMatrimonial.MARIE.value,
        "date_naissance": date(1987, 8, 9),
        "date_embauche": date(2017, 4, 1),
        "nationalite": "Congolaise",
        "poste": ("FIN", "MANAGER"),
        "is_staff": True,
        "salaire_base": Decimal("2400000"),
        "type_contrat": TypeContrat.CDI.value,
        "nombre_enfants": 3,
        "nom_conjoint": "Clarisse Ilunga",
    },
    {
        "prenom": "Sarah",
        "nom": "Mwanza",
        "matricule": "EMP-007",
        "email_personnel": "sarah.mwanza@example.com",
        "sexe": Sexe.FEMININ.value,
        "statut_matrimonial": StatutMatrimonial.MARIE.value,
        "date_naissance": date(1993, 12, 2),
        "date_embauche": date(2021, 11, 1),
        "nationalite": "Congolaise",
        "poste": ("FIN", "EMPLOYEE"),
        "salaire_base": Decimal("1350000"),
        "type_contrat": TypeContrat.CDD.value,
        "nombre_enfants": 1,
        "nom_conjoint": "Jonathan Mwanza",
    },
    {
        "prenom": "Olivier",
        "nom": "Tshisekedi",
        "matricule": "EMP-008",
        "email_personnel": "olivier.tshisekedi@example.com",
        "sexe": Sexe.MASCULIN.value,
        "statut_matrimonial": StatutMatrimonial.CELIBATAIRE.value,
        "date_naissance": date(1998, 5, 25),
        "date_embauche": date(2024, 2, 12),
        "nationalite": "Congolaise",
        "poste": ("OPS", "EMPLOYEE"),
        "salaire_base": Decimal("1100000"),
        "type_contrat": TypeContrat.STAGE.value,
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _employee_common(payload: dict[str, Any]) -> dict[str, Any]:
    """Fill the mandatory employee fields that are the same for every row."""
    return {
        "banque": "Rawbank",
        "numero_compte": f"RAW-{payload['matricule']}",
        "niveau_etude": "Licence",
        "numero_inss": f"INSS-{payload['matricule']}",
        "telephone_personnel": "+243900000000",
        "adresse_ligne1": "Avenue de la Paix",
        "ville": "Kinshasa",
        "pays": "RDC",
        "nom_contact_urgence": "Famille",
        "lien_contact_urgence": "Parent",
        "telephone_contact_urgence": "+243900000001",
        "nombre_enfants": payload.get("nombre_enfants", 0),
        "nom_conjoint": payload.get("nom_conjoint"),
        "statut_emploi": StatutEmploi.ACTIVE.value,
    }


async def _get_or_create_service(
    db: AsyncSession, payload: dict[str, str]
) -> Service:
    result = await db.execute(select(Service).where(Service.code == payload["code"]))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing
    svc = Service(code=payload["code"], titre=payload["titre"])
    db.add(svc)
    await db.flush()
    return svc


async def _get_or_create_group(db: AsyncSession, payload: dict[str, str]) -> Group:
    result = await db.execute(select(Group).where(Group.code == payload["code"]))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing
    grp = Group(code=payload["code"], name=payload["name"])
    db.add(grp)
    await db.flush()
    return grp


async def _get_or_create_service_group(
    db: AsyncSession, service_id: int, group_id: int
) -> ServiceGroup:
    stmt = select(ServiceGroup).where(
        ServiceGroup.service_id == service_id,
        ServiceGroup.group_id == group_id,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    poste = ServiceGroup(service_id=service_id, group_id=group_id)
    db.add(poste)
    await db.flush()
    return poste


async def _get_or_create_employe(
    db: AsyncSession, payload: dict[str, Any], poste_id: int
) -> Employe:
    stmt = select(Employe).where(Employe.matricule == payload["matricule"])
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    employe = Employe(
        prenom=payload["prenom"],
        nom=payload["nom"],
        postnom=payload.get("postnom"),
        matricule=payload["matricule"],
        date_naissance=payload["date_naissance"],
        sexe=payload["sexe"],
        statut_matrimonial=payload["statut_matrimonial"],
        nationalite=payload["nationalite"],
        email_personnel=payload["email_personnel"],
        date_embauche=payload["date_embauche"],
        poste_id=poste_id,
        **_employee_common(payload),
    )
    db.add(employe)
    await db.flush()
    return employe


async def _get_or_create_user(
    db: AsyncSession, employe: Employe, payload: dict[str, Any]
) -> User:
    stmt = select(User).where(User.email == payload["email_personnel"])
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    user = User(
        email=payload["email_personnel"],
        password=get_password_hash(DEFAULT_PASSWORD),
        nom=payload["nom"],
        prenom=payload["prenom"],
        is_active=True,
        is_superuser=payload.get("is_superuser", False),
        is_staff=payload.get("is_staff", False),
        employe_id=employe.id,
    )
    db.add(user)
    await db.flush()
    return user


async def _get_or_create_contrat(
    db: AsyncSession, employe: Employe, payload: dict[str, Any]
) -> Contrat:
    stmt = (
        select(Contrat)
        .where(Contrat.employe_id == employe.id)
        .where(Contrat.is_active.is_(True))
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    base = payload["salaire_base"]
    contrat = Contrat(
        employe_id=employe.id,
        type_contrat=payload["type_contrat"],
        date_debut=payload["date_embauche"],
        date_fin=None,
        salaire_base=base,
        indemnite_logement=base * Decimal("0.15"),
        indemnite_transport=Decimal("50000"),
        indemnite_fonction=base * Decimal("0.05"),
        prime_fonction=Decimal("0"),
        autre_avantage=Decimal("0"),
        assurance_patronale=base * Decimal("0.03"),
        assurance_salariale=base * Decimal("0.005"),
        fpc_patronale=base * Decimal("0.02"),
        fpc_salariale=Decimal("0"),
        devise="CDF",
        is_active=True,
    )
    db.add(contrat)
    await db.flush()
    return contrat


async def _link_user_to_group(db: AsyncSession, user_id: int, group: Group) -> None:
    stmt = select(UserGroup).where(
        UserGroup.user_id == user_id,
        UserGroup.group_id == group.id,
    )
    if (await db.execute(stmt)).scalar_one_or_none() is not None:
        return
    db.add(UserGroup(user_id=user_id, group_id=group.id))
    await db.flush()


# ---------------------------------------------------------------------------
# Conge mock data
# ---------------------------------------------------------------------------


async def _seed_soldes(db: AsyncSession, employes: list[Employe]) -> None:
    """Attribue un solde annuel par type de congé à chaque employé."""
    annee = date.today().year
    types = (await db.execute(select(TypeConge))).scalars().all()
    for employe in employes:
        for type_conge in types:
            stmt = select(SoldeConge).where(
                SoldeConge.employe_id == employe.id,
                SoldeConge.type_conge_id == type_conge.id,
                SoldeConge.annee == annee,
            )
            if (await db.execute(stmt)).scalar_one_or_none():
                continue
            alloue = type_conge.nb_jours_max_par_an or 0.0
            db.add(
                SoldeConge(
                    employe_id=employe.id,
                    type_conge_id=type_conge.id,
                    annee=annee,
                    alloue=alloue,
                    utilise=0.0,
                    restant=alloue,
                    reporte=0.0,
                )
            )
    await db.flush()


async def _seed_demandes(db: AsyncSession, employes: list[Employe]) -> None:
    """Ajoute 2 demandes de congé en attente sur 2 employés différents."""
    if len(employes) < 2:
        return
    type_ca = (
        await db.execute(select(TypeConge).where(TypeConge.code == "CA"))
    ).scalar_one_or_none()
    if type_ca is None:
        return
    etape = (
        await db.execute(
            select(EtapeProcessus)
            .where(EtapeProcessus.code_processus == CodeProcessus.CONGE.value)
            .where(EtapeProcessus.ordre == 1)
        )
    ).scalar_one_or_none()
    statut_en_attente = (
        await db.execute(
            select(StatutProcessus).where(
                StatutProcessus.code_statut == CodeStatut.EN_ATTENTE.value
            )
        )
    ).scalar_one_or_none()
    if etape is None or statut_en_attente is None:
        return

    samples = [
        {
            "employe": employes[1],
            "start_offset": 30,
            "duration": 5,
        },
        {
            "employe": employes[4] if len(employes) > 4 else employes[2],
            "start_offset": 45,
            "duration": 3,
        },
    ]
    for sample in samples:
        debut = date.today() + timedelta(days=sample["start_offset"])
        fin = debut + timedelta(days=sample["duration"] - 1)
        stmt = select(DemandeConge).where(
            DemandeConge.employe_id == sample["employe"].id,
            DemandeConge.date_debut == debut,
            DemandeConge.date_fin == fin,
        )
        if (await db.execute(stmt)).scalar_one_or_none():
            continue
        db.add(
            DemandeConge(
                employe_id=sample["employe"].id,
                type_conge_id=type_ca.id,
                date_debut=debut,
                date_fin=fin,
                nb_jours_ouvres=float(sample["duration"]),
                etape_courante_id=etape.id,
                statut_global_id=statut_en_attente.id,
                date_soumission=datetime.utcnow(),
            )
        )
    await db.flush()


# ---------------------------------------------------------------------------
# Paie mock data
# ---------------------------------------------------------------------------


async def _seed_periode_with_entrees(
    db: AsyncSession, employes: list[Employe], annee: int, mois: int
) -> PeriodePaie:
    stmt = select(PeriodePaie).where(
        PeriodePaie.annee == annee, PeriodePaie.mois == mois
    )
    periode = (await db.execute(stmt)).scalar_one_or_none()
    if periode is None:
        date_debut = date(annee, mois, 1)
        if mois == 12:
            date_fin = date(annee, 12, 31)
        else:
            date_fin = date(annee, mois + 1, 1) - timedelta(days=1)
        periode = PeriodePaie(
            annee=annee,
            mois=mois,
            date_debut=date_debut,
            date_fin=date_fin,
            statut=PeriodeStatutTexte.DRAFT.value,
        )
        db.add(periode)
        await db.flush()

    # Build one entree per active contract (idempotent on UNIQUE(employe,periode)).
    for employe in employes:
        contrat = (
            await db.execute(
                select(Contrat)
                .where(Contrat.employe_id == employe.id)
                .where(Contrat.is_active.is_(True))
            )
        ).scalar_one_or_none()
        if contrat is None:
            continue
        exists = (
            await db.execute(
                select(EntreePaie).where(
                    EntreePaie.employe_id == employe.id,
                    EntreePaie.periode_paie_id == periode.id,
                )
            )
        ).scalar_one_or_none()
        if exists is not None:
            continue
        salaire_brut = (
            contrat.salaire_base
            + contrat.indemnite_logement
            + contrat.indemnite_transport
            + contrat.indemnite_fonction
        )
        charges_salariales = contrat.assurance_salariale
        salaire_net = salaire_brut - charges_salariales
        db.add(
            EntreePaie(
                employe_id=employe.id,
                periode_paie_id=periode.id,
                contrat_reference={"contrat_id": contrat.id, "salaire_base": str(contrat.salaire_base)},
                salaire_base=contrat.salaire_base,
                indemnite_logement=contrat.indemnite_logement,
                indemnite_deplacement=contrat.indemnite_transport,
                indemnite_fonction=contrat.indemnite_fonction,
                allocation_familiale=Decimal("0"),
                autres_avantages=Decimal("0"),
                salaire_brut=salaire_brut,
                cotisations_patronales={
                    "inss_pension": str(contrat.assurance_patronale),
                },
                cotisations_salariales={
                    "inss_pension": str(contrat.assurance_salariale),
                },
                retenues_diverses={},
                total_charge_salariale=charges_salariales,
                base_imposable=salaire_brut - charges_salariales,
                salaire_net=salaire_net,
            )
        )
    await db.flush()
    return periode


async def _seed_retenues(db: AsyncSession, employes: list[Employe]) -> None:
    """Ajoute une retenue type 'avance' sur 2 employés."""
    for employe in employes[:2]:
        stmt = select(RetenueEmploye).where(
            RetenueEmploye.employe_id == employe.id,
            RetenueEmploye.type_retenue == DeductionType.AVANCE_SALAIRE.value,
        )
        if (await db.execute(stmt)).scalar_one_or_none():
            continue
        db.add(
            RetenueEmploye(
                employe_id=employe.id,
                type_retenue=DeductionType.AVANCE_SALAIRE.value,
                description="Avance sur salaire",
                montant_mensuel=Decimal("100000"),
                montant_total=Decimal("500000"),
                montant_deja_deduit=Decimal("0"),
                date_debut=date.today().replace(day=1),
                est_active=True,
                est_recurrente=True,
            )
        )
    await db.flush()


async def _seed_alerts(db: AsyncSession, periode: PeriodePaie) -> None:
    samples = [
        {
            "alert_type": AlertType.VALIDATION_ERROR.value,
            "severity": AlertSeverity.HIGH.value,
            "title": "Valeurs de cotisations manquantes",
            "message": "Vérifier les cotisations patronales de la période.",
        },
        {
            "alert_type": AlertType.OTHER.value,
            "severity": AlertSeverity.LOW.value,
            "title": "Rappel — clôture de période",
            "message": "Cette période de paie doit être clôturée avant la fin du mois.",
        },
    ]
    for sample in samples:
        stmt = select(Alert).where(
            Alert.periode_paie_id == periode.id,
            Alert.title == sample["title"],
        )
        if (await db.execute(stmt)).scalar_one_or_none():
            continue
        db.add(
            Alert(
                periode_paie_id=periode.id,
                status=AlertStatus.ACTIVE.value,
                details={},
                **sample,
            )
        )
    await db.flush()


# ---------------------------------------------------------------------------
# Reset (delete mock data)
# ---------------------------------------------------------------------------


async def _reset_mock_data(db: AsyncSession, verbose: bool) -> None:
    matricules = [p["matricule"] for p in EMPLOYEES]
    emails = [p["email_personnel"] for p in EMPLOYEES]

    # Pull IDs first so we can cascade-delete cleanly.
    employe_ids = [
        row[0]
        for row in (
            await db.execute(
                select(Employe.id).where(Employe.matricule.in_(matricules))
            )
        ).all()
    ]
    if verbose:
        print(f"  • removing mock data for {len(employe_ids)} employe(s)")

    if employe_ids:
        # Paie-related rows first (FKs point to employe & periode)
        await db.execute(
            delete(EntreePaie).where(EntreePaie.employe_id.in_(employe_ids))
        )
        await db.execute(
            delete(RetenueEmploye).where(RetenueEmploye.employe_id.in_(employe_ids))
        )
        await db.execute(
            delete(Alert).where(Alert.employe_id.in_(employe_ids))
        )
        # Conge-related
        await db.execute(
            delete(DemandeConge).where(DemandeConge.employe_id.in_(employe_ids))
        )
        await db.execute(
            delete(SoldeConge).where(SoldeConge.employe_id.in_(employe_ids))
        )
        # User account + employe + contrat (contrat cascades from employe)
        await db.execute(delete(User).where(User.email.in_(emails)))
        await db.execute(delete(Employe).where(Employe.id.in_(employe_ids)))

    # Periode de paie seed (year/month pair used below)
    today = date.today()
    await db.execute(
        delete(PeriodePaie).where(
            PeriodePaie.annee == today.year,
            PeriodePaie.mois == today.month,
        )
    )
    await db.commit()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def seed(reset: bool = False, verbose: bool = True) -> None:
    def log(msg: str) -> None:
        if verbose:
            print(msg)

    async with AsyncSessionLocal() as db:
        if reset:
            log("🔄 Resetting mock data...")
            await _reset_mock_data(db, verbose=verbose)

        # 1. Services / groups / postes
        log("🏢 Seeding services + groups + postes...")
        services = {p["code"]: await _get_or_create_service(db, p) for p in SERVICES}
        groups = {p["code"]: await _get_or_create_group(db, p) for p in GROUPS}
        postes: dict[tuple[str, str], ServiceGroup] = {}
        for svc_code, grp_code in POSTES:
            postes[(svc_code, grp_code)] = await _get_or_create_service_group(
                db, services[svc_code].id, groups[grp_code].id
            )

        # 2. Conge / paie default workflow (idempotent)
        log("⚙️  Ensuring CONGE + PAIE workflow defaults...")
        await init_conge_defaults(db)
        await init_paie_workflow_defaults(db)

        # 3. Employees + users + contrats
        log(f"👤 Seeding {len(EMPLOYEES)} employees + user accounts...")
        employes: list[Employe] = []
        for payload in EMPLOYEES:
            poste = postes[payload["poste"]]
            employe = await _get_or_create_employe(db, payload, poste.id)
            user = await _get_or_create_user(db, employe, payload)
            await _get_or_create_contrat(db, employe, payload)
            # Attach user to the group implied by its poste.
            _, grp_code = payload["poste"]
            await _link_user_to_group(db, user.id, groups[grp_code])
            employes.append(employe)

        # Commit employees before setting responsables, so FKs resolve.
        await db.commit()

        # 4. Hierarchy: first employee becomes the manager of every other
        if employes:
            boss = employes[0]
            for subordinate in employes[1:]:
                if subordinate.responsable_id is None:
                    subordinate.responsable_id = boss.id
            await db.commit()

        # 5. Conge seed data
        log("🏖️  Seeding conge soldes + sample demandes...")
        await _seed_soldes(db, employes)
        await _seed_demandes(db, employes)
        await db.commit()

        # 6. Paie seed data
        today = date.today()
        log(f"💰 Seeding paie periode {today.year}-{today.month:02d}...")
        periode = await _seed_periode_with_entrees(
            db, employes, today.year, today.month
        )
        await _seed_retenues(db, employes)
        await _seed_alerts(db, periode)
        await db.commit()

        log("\n✅ Mock data seeding complete.")
        log(f"   - {len(employes)} employees / users (password: {DEFAULT_PASSWORD!r})")
        log(f"   - period de paie {periode.annee}-{periode.mois:02d} ({len(employes)} entrees)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete mock rows matching the seed fixtures before re-inserting.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output.",
    )
    args = parser.parse_args()
    asyncio.run(seed(reset=args.reset, verbose=not args.quiet))


if __name__ == "__main__":
    main()
