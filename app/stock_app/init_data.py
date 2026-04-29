"""Script d'initialisation des données par défaut du module stock.

Crée (de manière idempotente) :
- Les statuts génériques de processus (réutilise ceux de conge_app si déjà
  créés) — ``EN_ATTENTE``, ``EN_COURS``, ``VALIDE``, ``REJETE``, ``ANNULE``.
- Les unités de mesure par défaut (PIECE, KG, LITRE, PAQUET).
- Les catégories d'articles par défaut (CONSO, EPI, EQUIPEMENT, BUREAU).
- Les étapes du workflow pour chaque processus seedé
  (``STOCK_SORTIE``, ``STOCK_ENTREE``, ``STOCK_AJUSTEMENT``).
- Les actions ``APPROUVER`` / ``REJETER`` associées à chaque étape.

Tout est strictement éditable en DB après le seed (workflow dynamique).
Les entités déjà existantes ne sont pas écrasées.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conge_app.models import (
    ActionEtapeProcessus,
    EtapeProcessus,
    StatutProcessus,
)
from app.stock_app.constants import (
    CodeProcessusStock,
    CodeStatutStock,
    NomActionStock,
)
from app.stock_app.models import CategorieArticle, UniteMesure


DEFAULT_STATUTS: list[str] = [statut.value for statut in CodeStatutStock]


DEFAULT_UNITES: list[dict] = [
    {"code": "PCE", "libelle": "Pièce"},
    {"code": "KG", "libelle": "Kilogramme"},
    {"code": "L", "libelle": "Litre"},
    {"code": "PQT", "libelle": "Paquet"},
]


DEFAULT_CATEGORIES: list[dict] = [
    {"code": "CONSO", "nom": "Consommables", "description": "Fournitures consommables (papier, encre, etc.)"},
    {"code": "EPI", "nom": "Équipements de protection", "description": "EPI (casques, gants, chaussures de sécurité)"},
    {"code": "EQUIPEMENT", "nom": "Équipement", "description": "Matériel durable (ordinateurs, mobilier)"},
    {"code": "BUREAU", "nom": "Bureau", "description": "Petits articles de bureau"},
]


# Étapes par défaut, identiques pour les 3 processus stock pour MVP :
# (ordre, nom, is_responsable). Configurable en DB après init.
DEFAULT_ETAPES_PAR_PROCESSUS: dict[str, list[dict]] = {
    CodeProcessusStock.SORTIE.value: [
        {"ordre": 1, "nom_etape": "Validation Responsable N+1", "is_responsable": True},
        {"ordre": 2, "nom_etape": "Validation Magasinier", "is_responsable": False},
    ],
    CodeProcessusStock.ENTREE.value: [
        {"ordre": 1, "nom_etape": "Validation Magasinier", "is_responsable": False},
    ],
    CodeProcessusStock.AJUSTEMENT.value: [
        {"ordre": 1, "nom_etape": "Validation Magasinier", "is_responsable": False},
        {"ordre": 2, "nom_etape": "Validation RH", "is_responsable": False},
    ],
}


async def _ensure_statut(db: AsyncSession, code_statut: str) -> StatutProcessus:
    stmt = select(StatutProcessus).where(StatutProcessus.code_statut == code_statut)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    statut = StatutProcessus(code_statut=code_statut)
    db.add(statut)
    await db.flush()
    return statut


async def _ensure_unite(db: AsyncSession, payload: dict) -> UniteMesure:
    stmt = select(UniteMesure).where(UniteMesure.code == payload["code"])
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    unite = UniteMesure(**payload)
    db.add(unite)
    await db.flush()
    return unite


async def _ensure_categorie(db: AsyncSession, payload: dict) -> CategorieArticle:
    stmt = select(CategorieArticle).where(CategorieArticle.code == payload["code"])
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    categorie = CategorieArticle(**payload)
    db.add(categorie)
    await db.flush()
    return categorie


async def _ensure_etape(
    db: AsyncSession,
    *,
    code_processus: str,
    ordre: int,
    nom_etape: str,
    is_responsable: bool,
    poste_id: int | None = None,
) -> EtapeProcessus:
    stmt = select(EtapeProcessus).where(
        EtapeProcessus.code_processus == code_processus,
        EtapeProcessus.ordre == ordre,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    etape = EtapeProcessus(
        code_processus=code_processus,
        ordre=ordre,
        nom_etape=nom_etape,
        is_responsable=is_responsable,
        poste_id=poste_id,
    )
    db.add(etape)
    await db.flush()
    return etape


async def _ensure_action(
    db: AsyncSession,
    *,
    etape_id: int,
    nom_action: str,
    statut_cible_id: int,
    etape_suivante_id: int | None,
) -> ActionEtapeProcessus:
    stmt = select(ActionEtapeProcessus).where(
        ActionEtapeProcessus.etape_id == etape_id,
        ActionEtapeProcessus.nom_action == nom_action,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    action = ActionEtapeProcessus(
        etape_id=etape_id,
        nom_action=nom_action,
        statut_cible_id=statut_cible_id,
        etape_suivante_id=etape_suivante_id,
    )
    db.add(action)
    await db.flush()
    return action


async def init_stock_defaults(db: AsyncSession) -> None:
    """Initialise les données par défaut pour le module stock.

    Idempotent : peut être lancé à chaque démarrage sans écraser l'existant.
    """
    # 1. Statuts génériques (mutualisés avec conge / paie)
    statuts: dict[str, StatutProcessus] = {}
    for code in DEFAULT_STATUTS:
        statuts[code] = await _ensure_statut(db, code)

    # 2. Unités de mesure
    for payload in DEFAULT_UNITES:
        await _ensure_unite(db, payload)

    # 3. Catégories
    for payload in DEFAULT_CATEGORIES:
        await _ensure_categorie(db, payload)

    # 4. Étapes + actions pour chaque processus
    for code_processus, etapes_def in DEFAULT_ETAPES_PAR_PROCESSUS.items():
        etapes: list[EtapeProcessus] = []
        for etape_def in etapes_def:
            etape = await _ensure_etape(
                db,
                code_processus=code_processus,
                ordre=etape_def["ordre"],
                nom_etape=etape_def["nom_etape"],
                is_responsable=etape_def["is_responsable"],
            )
            etapes.append(etape)

        # Actions par étape
        for index, etape in enumerate(etapes):
            etape_suivante = etapes[index + 1] if index + 1 < len(etapes) else None

            # APPROUVER : VALIDE en terminal, EN_COURS sinon
            statut_approuver = (
                statuts[CodeStatutStock.VALIDE.value]
                if etape_suivante is None
                else statuts[CodeStatutStock.EN_COURS.value]
            )
            await _ensure_action(
                db,
                etape_id=etape.id,
                nom_action=NomActionStock.APPROUVER.value,
                statut_cible_id=statut_approuver.id,
                etape_suivante_id=etape_suivante.id if etape_suivante else None,
            )

            # REJETER : toujours terminal → REJETE
            await _ensure_action(
                db,
                etape_id=etape.id,
                nom_action=NomActionStock.REJETER.value,
                statut_cible_id=statuts[CodeStatutStock.REJETE.value].id,
                etape_suivante_id=None,
            )
