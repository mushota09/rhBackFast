"""FastAPI routes for the workflow-based stock management module."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conge_app.models import (
    ActionEtapeProcessus,
    DemandeAttribution,
    EtapeProcessus,
    HistoriqueDemande,
    StatutProcessus,
)
from app.conge_app.services.attribution_service import AttributionService
from app.core.database import get_db
from app.core.permissions import require_permission
from app.core.query_utils import apply_expansion, parse_expand_param
from app.stock_app.constants import (
    CodeProcessusStock,
    DemandeTypeStock,
)
from app.stock_app.models import (
    Article,
    AttributionMateriel,
    CategorieArticle,
    DemandeStock,
    MouvementStock,
    UniteMesure,
)
from app.stock_app.schemas import (
    ActionEtapeCreate,
    ActionEtapeResponse,
    ActionEtapeUpdate,
    ActionsPossiblesResponse,
    AppliquerActionRequest,
    ArticleCreate,
    ArticleResponse,
    ArticleUpdate,
    AttributionMaterielResponse,
    AttributionMaterielReturn,
    AttributionResponse,
    CategorieCreate,
    CategorieResponse,
    CategorieUpdate,
    DemandeStockCreate,
    DemandeStockResponse,
    EtapeProcessusCreate,
    EtapeProcessusResponse,
    EtapeProcessusUpdate,
    HistoriqueResponse,
    MouvementManuelRequest,
    MouvementResponse,
    PaginatedArticle,
    PaginatedAttributionMateriel,
    PaginatedCategorie,
    PaginatedDemandeStock,
    PaginatedMouvement,
    PaginatedStockEtat,
    PaginatedUniteMesure,
    StatutProcessusCreate,
    StatutProcessusResponse,
    StockEtatLigne,
    UniteMesureCreate,
    UniteMesureResponse,
    UniteMesureUpdate,
)
from app.stock_app.services import (
    AttributionMaterielService,
    DemandeStockService,
    MouvementStockService,
    StockWorkflowConfigError,
    StockWorkflowPermissionError,
    StockWorkflowService,
    StockWorkflowStateError,
)
from app.stock_app.services.stock_service import (
    StockInsuffisantError,
    lister_etat_stock,
)
from app.user_app.models import User


router = APIRouter(prefix="/api/stock", tags=["Stock Management"])


# ---------------------------------------------------------------------------
# Utilitaires internes
# ---------------------------------------------------------------------------


def _resolve_employe_id(current_user: User) -> int:
    if current_user.employe_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Votre compte utilisateur n'est lié à aucun employé",
        )
    return current_user.employe_id


# ---------------------------------------------------------------------------
# Catégories
# ---------------------------------------------------------------------------


@router.get("/categories", response_model=PaginatedCategorie)
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    actif: Optional[bool] = Query(None),
):
    stmt = select(CategorieArticle)
    count_stmt = select(func.count()).select_from(CategorieArticle)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(CategorieArticle.nom.ilike(like), CategorieArticle.code.ilike(like)))
        count_stmt = count_stmt.where(
            or_(CategorieArticle.nom.ilike(like), CategorieArticle.code.ilike(like))
        )
    if actif is not None:
        stmt = stmt.where(CategorieArticle.actif.is_(actif))
        count_stmt = count_stmt.where(CategorieArticle.actif.is_(actif))
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(CategorieArticle.nom.asc()).offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().all()
    return PaginatedCategorie(
        items=[CategorieResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/categories", response_model=CategorieResponse, status_code=status.HTTP_201_CREATED
)
async def create_categorie(
    payload: CategorieCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    existing = (
        await db.execute(select(CategorieArticle).where(CategorieArticle.code == payload.code))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Une catégorie avec le code '{payload.code}' existe déjà",
        )
    categorie = CategorieArticle(**payload.model_dump())
    db.add(categorie)
    await db.commit()
    await db.refresh(categorie)
    return categorie


@router.patch("/categories/{categorie_id}", response_model=CategorieResponse)
async def update_categorie(
    categorie_id: int,
    payload: CategorieUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    categorie = await db.get(CategorieArticle, categorie_id)
    if categorie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(categorie, field, value)
    await db.commit()
    await db.refresh(categorie)
    return categorie


@router.delete("/categories/{categorie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categorie(
    categorie_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    categorie = await db.get(CategorieArticle, categorie_id)
    if categorie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    await db.delete(categorie)
    await db.commit()


# ---------------------------------------------------------------------------
# Unités de mesure
# ---------------------------------------------------------------------------


@router.get("/unites", response_model=PaginatedUniteMesure)
async def list_unites(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    stmt = select(UniteMesure).order_by(UniteMesure.code.asc())
    count_stmt = select(func.count()).select_from(UniteMesure)
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().all()
    return PaginatedUniteMesure(
        items=[UniteMesureResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/unites", response_model=UniteMesureResponse, status_code=status.HTTP_201_CREATED
)
async def create_unite(
    payload: UniteMesureCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    existing = (
        await db.execute(select(UniteMesure).where(UniteMesure.code == payload.code))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Une unité avec le code '{payload.code}' existe déjà",
        )
    unite = UniteMesure(**payload.model_dump())
    db.add(unite)
    await db.commit()
    await db.refresh(unite)
    return unite


@router.patch("/unites/{unite_id}", response_model=UniteMesureResponse)
async def update_unite(
    unite_id: int,
    payload: UniteMesureUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    unite = await db.get(UniteMesure, unite_id)
    if unite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unité introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(unite, field, value)
    await db.commit()
    await db.refresh(unite)
    return unite


@router.delete("/unites/{unite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unite(
    unite_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    unite = await db.get(UniteMesure, unite_id)
    if unite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unité introuvable")
    await db.delete(unite)
    await db.commit()


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------


@router.get("/articles", response_model=PaginatedArticle)
async def list_articles(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    categorie_id: Optional[int] = Query(None),
    actif: Optional[bool] = Query(None),
    expand: Optional[str] = Query(None, description="Relations à inclure (categorie, unite_mesure)"),
):
    stmt = select(Article)
    count_stmt = select(func.count()).select_from(Article)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Article.nom.ilike(like), Article.code.ilike(like)))
        count_stmt = count_stmt.where(or_(Article.nom.ilike(like), Article.code.ilike(like)))
    if categorie_id is not None:
        stmt = stmt.where(Article.categorie_id == categorie_id)
        count_stmt = count_stmt.where(Article.categorie_id == categorie_id)
    if actif is not None:
        stmt = stmt.where(Article.actif.is_(actif))
        count_stmt = count_stmt.where(Article.actif.is_(actif))
    total = (await db.execute(count_stmt)).scalar() or 0
    if expand:
        stmt = apply_expansion(stmt, Article, parse_expand_param(expand))
    stmt = stmt.order_by(Article.nom.asc()).offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().all()
    return PaginatedArticle(
        items=[ArticleResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED
)
async def create_article(
    payload: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    existing = (
        await db.execute(select(Article).where(Article.code == payload.code))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un article avec le code '{payload.code}' existe déjà",
        )
    article = Article(**payload.model_dump())
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


@router.patch("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    payload: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    article = await db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(article, field, value)
    await db.commit()
    await db.refresh(article)
    return article


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    article = await db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")
    await db.delete(article)
    await db.commit()


# ---------------------------------------------------------------------------
# État du stock courant
# ---------------------------------------------------------------------------


@router.get("/etat", response_model=PaginatedStockEtat)
async def stock_etat_courant(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    en_alerte_seulement: bool = Query(False),
    categorie_id: Optional[int] = Query(None),
):
    items, total = await lister_etat_stock(
        db,
        skip=skip,
        limit=limit,
        en_alerte_seulement=en_alerte_seulement,
        categorie_id=categorie_id,
    )
    return PaginatedStockEtat(
        items=[StockEtatLigne(**item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/alertes", response_model=PaginatedStockEtat)
async def stock_alertes(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    items, total = await lister_etat_stock(
        db, skip=skip, limit=limit, en_alerte_seulement=True
    )
    return PaginatedStockEtat(
        items=[StockEtatLigne(**item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Mouvements (lecture + ajustement manuel)
# ---------------------------------------------------------------------------


@router.get("/mouvements", response_model=PaginatedMouvement)
async def list_mouvements(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    article_id: Optional[int] = Query(None),
    type_mouvement: Optional[str] = Query(None),
    employe_attributaire_id: Optional[int] = Query(None),
):
    stmt = select(MouvementStock)
    count_stmt = select(func.count()).select_from(MouvementStock)
    if article_id is not None:
        stmt = stmt.where(MouvementStock.article_id == article_id)
        count_stmt = count_stmt.where(MouvementStock.article_id == article_id)
    if type_mouvement is not None:
        stmt = stmt.where(MouvementStock.type_mouvement == type_mouvement)
        count_stmt = count_stmt.where(MouvementStock.type_mouvement == type_mouvement)
    if employe_attributaire_id is not None:
        stmt = stmt.where(MouvementStock.employe_attributaire_id == employe_attributaire_id)
        count_stmt = count_stmt.where(
            MouvementStock.employe_attributaire_id == employe_attributaire_id
        )
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(MouvementStock.created_at.desc()).offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().all()
    return PaginatedMouvement(
        items=[MouvementResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/mouvements", response_model=MouvementResponse, status_code=status.HTTP_201_CREATED
)
async def create_mouvement_manuel(
    payload: MouvementManuelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("stock", "manage_articles")),
):
    """Ajustement manuel hors workflow (réservé aux gestionnaires de stock)."""
    employe_id = current_user.employe_id
    try:
        mvt = await MouvementStockService.enregistrer_mouvement(
            db,
            article_id=payload.article_id,
            type_mouvement=payload.type_mouvement.value,
            quantite=payload.quantite,
            auteur_id=employe_id,
            employe_attributaire_id=payload.employe_attributaire_id,
            commentaire=payload.commentaire,
        )
    except StockInsuffisantError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    await db.commit()
    await db.refresh(mvt)
    return mvt


# ---------------------------------------------------------------------------
# Demandes (workflow-driven)
# ---------------------------------------------------------------------------


@router.get("/demandes", response_model=PaginatedDemandeStock)
async def list_demandes(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    processus: Optional[str] = Query(None),
    demandeur_id: Optional[int] = Query(None),
    statut_global_id: Optional[int] = Query(None),
    expand: Optional[str] = Query(None, description="Relations à inclure (lignes)"),
):
    stmt = select(DemandeStock)
    count_stmt = select(func.count()).select_from(DemandeStock)
    if processus:
        stmt = stmt.where(DemandeStock.processus == processus)
        count_stmt = count_stmt.where(DemandeStock.processus == processus)
    if demandeur_id is not None:
        stmt = stmt.where(DemandeStock.demandeur_id == demandeur_id)
        count_stmt = count_stmt.where(DemandeStock.demandeur_id == demandeur_id)
    if statut_global_id is not None:
        stmt = stmt.where(DemandeStock.statut_global_id == statut_global_id)
        count_stmt = count_stmt.where(DemandeStock.statut_global_id == statut_global_id)
    total = (await db.execute(count_stmt)).scalar() or 0
    if expand:
        stmt = apply_expansion(stmt, DemandeStock, parse_expand_param(expand))
    stmt = stmt.order_by(DemandeStock.created_at.desc()).offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().unique().all()
    return PaginatedDemandeStock(
        items=[DemandeStockResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/demandes/me", response_model=PaginatedDemandeStock)
async def list_mes_demandes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("stock", "view")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    employe_id = _resolve_employe_id(current_user)
    stmt = (
        select(DemandeStock)
        .where(DemandeStock.demandeur_id == employe_id)
        .order_by(DemandeStock.created_at.desc())
    )
    count_stmt = (
        select(func.count())
        .select_from(DemandeStock)
        .where(DemandeStock.demandeur_id == employe_id)
    )
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().unique().all()
    return PaginatedDemandeStock(
        items=[DemandeStockResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/demandes/{demande_id}", response_model=DemandeStockResponse)
async def get_demande(
    demande_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
):
    demande = await db.get(DemandeStock, demande_id)
    if demande is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demande introuvable")
    await db.refresh(demande, attribute_names=["lignes"])
    return demande


@router.post(
    "/demandes", response_model=DemandeStockResponse, status_code=status.HTTP_201_CREATED
)
async def create_demande(
    payload: DemandeStockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("stock", "create_demande")),
):
    employe_id = _resolve_employe_id(current_user)
    responsable_id = None
    # Récupère le responsable hiérarchique de l'employé courant si existant.
    from app.user_app.models import Employe

    employe = await db.get(Employe, employe_id)
    if employe is not None:
        responsable_id = getattr(employe, "manager_id", None)

    try:
        demande = await DemandeStockService.creer_et_soumettre(
            db,
            processus=payload.processus.value,
            demandeur_id=employe_id,
            responsable_id=responsable_id,
            motif=payload.motif,
            employe_beneficiaire_id=payload.employe_beneficiaire_id,
            lignes=[ligne.model_dump() for ligne in payload.lignes],
        )
    except StockWorkflowConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except (StockWorkflowStateError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    await db.commit()
    await db.refresh(demande, attribute_names=["lignes"])
    return demande


@router.get(
    "/demandes/{demande_id}/actions", response_model=ActionsPossiblesResponse
)
async def actions_possibles(
    demande_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("stock", "view")),
):
    demande = await db.get(DemandeStock, demande_id)
    if demande is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demande introuvable")
    if demande.etape_courante_id is None:
        return ActionsPossiblesResponse(actions=[], is_valideur=False)
    actions = await StockWorkflowService.list_actions_for_etape(
        db, demande.etape_courante_id
    )
    employe_id = current_user.employe_id
    is_valideur = False
    if employe_id is not None:
        is_valideur = await StockWorkflowService.is_user_valideur(
            db, demande, employe_id
        )
    return ActionsPossiblesResponse(
        actions=[ActionEtapeResponse.model_validate(a) for a in actions],
        is_valideur=is_valideur,
    )


@router.post("/demandes/{demande_id}/take_ownership", response_model=AttributionResponse)
async def take_ownership(
    demande_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("stock", "approve_demande")),
):
    employe_id = _resolve_employe_id(current_user)
    demande = await db.get(DemandeStock, demande_id)
    if demande is None or demande.etape_courante_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande introuvable ou non soumise",
        )
    try:
        attribution = await AttributionService.take_ownership(
            db,
            demande_id=demande.id,
            etape_id=demande.etape_courante_id,
            employe_id=employe_id,
            demande_type=DemandeTypeStock.DEMANDE_STOCK.value,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    await db.commit()
    await db.refresh(attribution)
    return attribution


@router.post("/demandes/{demande_id}/actions", response_model=DemandeStockResponse)
async def appliquer_action(
    demande_id: int,
    payload: AppliquerActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("stock", "approve_demande")),
):
    employe_id = _resolve_employe_id(current_user)
    demande = await db.get(DemandeStock, demande_id)
    if demande is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demande introuvable")
    try:
        demande = await StockWorkflowService.apply_action(
            db,
            demande,
            action_id=payload.action_id,
            valideur_employe_id=employe_id,
            commentaire=payload.commentaire,
        )
    except StockWorkflowPermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except StockInsuffisantError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except (StockWorkflowStateError, StockWorkflowConfigError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    await db.commit()
    await db.refresh(demande, attribute_names=["lignes"])
    return demande


@router.get(
    "/demandes/{demande_id}/historique", response_model=list[HistoriqueResponse]
)
async def get_historique(
    demande_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
):
    stmt = (
        select(HistoriqueDemande)
        .where(
            HistoriqueDemande.demande_type == DemandeTypeStock.DEMANDE_STOCK.value,
            HistoriqueDemande.demande_id == demande_id,
        )
        .order_by(HistoriqueDemande.created_at.asc())
    )
    items = (await db.execute(stmt)).scalars().all()
    return [HistoriqueResponse.model_validate(i) for i in items]


@router.get(
    "/demandes/{demande_id}/attributions", response_model=list[AttributionResponse]
)
async def get_attributions(
    demande_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
):
    stmt = (
        select(DemandeAttribution)
        .where(
            DemandeAttribution.demande_type == DemandeTypeStock.DEMANDE_STOCK.value,
            DemandeAttribution.demande_id == demande_id,
        )
        .order_by(DemandeAttribution.date_attribution.asc())
    )
    items = (await db.execute(stmt)).scalars().all()
    return [AttributionResponse.model_validate(i) for i in items]


# ---------------------------------------------------------------------------
# Attribution matériel (suivi 'qui possède quoi')
# ---------------------------------------------------------------------------


@router.get("/attributions-materiel", response_model=PaginatedAttributionMateriel)
async def list_attributions_materiel(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view_attributions")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    employe_id: Optional[int] = Query(None),
    article_id: Optional[int] = Query(None),
    actif: Optional[bool] = Query(None),
):
    stmt = select(AttributionMateriel)
    count_stmt = select(func.count()).select_from(AttributionMateriel)
    if employe_id is not None:
        stmt = stmt.where(AttributionMateriel.employe_id == employe_id)
        count_stmt = count_stmt.where(AttributionMateriel.employe_id == employe_id)
    if article_id is not None:
        stmt = stmt.where(AttributionMateriel.article_id == article_id)
        count_stmt = count_stmt.where(AttributionMateriel.article_id == article_id)
    if actif is not None:
        stmt = stmt.where(AttributionMateriel.actif.is_(actif))
        count_stmt = count_stmt.where(AttributionMateriel.actif.is_(actif))
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(AttributionMateriel.date_attribution.desc()).offset(skip).limit(limit)
    items = (await db.execute(stmt)).scalars().all()
    return PaginatedAttributionMateriel(
        items=[AttributionMaterielResponse.model_validate(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/attributions-materiel/me", response_model=list[AttributionMaterielResponse])
async def mes_attributions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("stock", "view")),
    actif_seulement: bool = Query(True),
):
    employe_id = _resolve_employe_id(current_user)
    items = await AttributionMaterielService.lister_par_employe(
        db, employe_id, actif_seulement=actif_seulement
    )
    return [AttributionMaterielResponse.model_validate(i) for i in items]


@router.post(
    "/attributions-materiel/{attribution_id}/retour",
    response_model=AttributionMaterielResponse,
)
async def marquer_retour(
    attribution_id: int,
    payload: AttributionMaterielReturn,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_articles")),
):
    try:
        attribution = await AttributionMaterielService.marquer_retour(
            db, attribution_id, commentaire=payload.commentaire
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    await db.commit()
    await db.refresh(attribution)
    return attribution


# ---------------------------------------------------------------------------
# Configuration runtime du workflow (admin)
# ---------------------------------------------------------------------------


@router.get("/workflow/statuts", response_model=list[StatutProcessusResponse])
async def list_statuts(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
):
    stmt = select(StatutProcessus).order_by(StatutProcessus.code_statut.asc())
    items = (await db.execute(stmt)).scalars().all()
    return [StatutProcessusResponse.model_validate(i) for i in items]


@router.post(
    "/workflow/statuts",
    response_model=StatutProcessusResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_statut(
    payload: StatutProcessusCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_workflow")),
):
    existing = (
        await db.execute(select(StatutProcessus).where(StatutProcessus.code_statut == payload.code_statut))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Le statut '{payload.code_statut}' existe déjà",
        )
    statut = StatutProcessus(code_statut=payload.code_statut)
    db.add(statut)
    await db.commit()
    await db.refresh(statut)
    return statut


@router.get("/workflow/etapes", response_model=list[EtapeProcessusResponse])
async def list_etapes(
    code_processus: Optional[str] = Query(
        None, description="Filtre sur un code processus (STOCK_SORTIE, STOCK_ENTREE, …)"
    ),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
):
    stmt = select(EtapeProcessus)
    if code_processus is not None:
        stmt = stmt.where(EtapeProcessus.code_processus == code_processus)
    else:
        # Limiter aux codes du module stock par défaut.
        stmt = stmt.where(
            EtapeProcessus.code_processus.in_([p.value for p in CodeProcessusStock])
        )
    stmt = stmt.order_by(EtapeProcessus.code_processus.asc(), EtapeProcessus.ordre.asc())
    items = (await db.execute(stmt)).scalars().all()
    return [EtapeProcessusResponse.model_validate(i) for i in items]


@router.post(
    "/workflow/etapes",
    response_model=EtapeProcessusResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_etape(
    payload: EtapeProcessusCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_workflow")),
):
    etape = EtapeProcessus(**payload.model_dump())
    db.add(etape)
    await db.commit()
    await db.refresh(etape)
    return etape


@router.patch("/workflow/etapes/{etape_id}", response_model=EtapeProcessusResponse)
async def update_etape(
    etape_id: int,
    payload: EtapeProcessusUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_workflow")),
):
    etape = await db.get(EtapeProcessus, etape_id)
    if etape is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Étape introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(etape, field, value)
    await db.commit()
    await db.refresh(etape)
    return etape


@router.get("/workflow/etapes/{etape_id}/actions", response_model=list[ActionEtapeResponse])
async def list_actions_etape(
    etape_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "view")),
):
    items = await StockWorkflowService.list_actions_for_etape(db, etape_id)
    return [ActionEtapeResponse.model_validate(i) for i in items]


@router.post(
    "/workflow/actions",
    response_model=ActionEtapeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_action(
    payload: ActionEtapeCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_workflow")),
):
    action = ActionEtapeProcessus(**payload.model_dump())
    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action


@router.patch("/workflow/actions/{action_id}", response_model=ActionEtapeResponse)
async def update_action(
    action_id: int,
    payload: ActionEtapeUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_workflow")),
):
    action = await db.get(ActionEtapeProcessus, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(action, field, value)
    await db.commit()
    await db.refresh(action)
    return action


@router.delete("/workflow/actions/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(
    action_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("stock", "manage_workflow")),
):
    action = await db.get(ActionEtapeProcessus, action_id)
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable")
    await db.delete(action)
    await db.commit()
