from fastapi import APIRouter, Depends, Query, Request

from app.adapters.input.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    CareerResponse,
    CatalogResponse,
    ComparisonRequest,
    ComparisonResponse,
)
from app.application.analyze import AnalyzeComparison
from app.application.catalog import Catalog
from app.application.compare import CompareCareers
from app.infrastructure.dependencies import catalog_dependency
from app.ports.careers import CatalogQuery

router = APIRouter(prefix="/api")


@router.post("/comparaciones/analisis", response_model=AnalysisResponse)
def analysis(
    body: AnalysisRequest, request: Request, catalog: Catalog = Depends(catalog_dependency)
):
    result = AnalyzeComparison(
        catalog, request.app.state.analysis_service, request.app.state.recommendation_service
    ).execute(body.career_ids, body.preferences.model_dump(exclude_none=True))
    result["recommendations"] = [
        CareerResponse.model_validate(c) for c in result["recommendations"]
    ]
    return AnalysisResponse(**result)


@router.post("/comparaciones", response_model=ComparisonResponse)
def comparison(body: ComparisonRequest, catalog: Catalog = Depends(catalog_dependency)):
    return ComparisonResponse.model_validate(CompareCareers(catalog).execute(body.career_ids))


@router.get("/salud")
def health(request: Request):
    return {"status": "ok", "data_mode": request.app.state.settings.data_mode}


@router.get("/filtros", response_model=dict[str, list[str]])
def filters(catalog: Catalog = Depends(catalog_dependency)):
    return catalog.filters()


@router.get("/carreras", response_model=CatalogResponse)
def careers(
    request: Request,
    q: str = Query("", max_length=150),
    tipo: str = Query("", max_length=60),
    modalidad: str = Query("", max_length=100),
    ubicacion: str = Query("", max_length=200),
    pagina: int = Query(1, ge=1, le=10000),
    limite: int = Query(12, ge=1, le=100),
    catalog: Catalog = Depends(catalog_dependency),
):
    items, total = catalog.search(CatalogQuery(q, tipo, modalidad, ubicacion, pagina, limite))
    return CatalogResponse(
        items=[CareerResponse.model_validate(c) for c in items],
        total=total,
        pagina=pagina,
        limite=limite,
        data_mode=request.app.state.settings.data_mode,
    )


@router.get("/carreras/{id}", response_model=CareerResponse)
def detail(id: str, catalog: Catalog = Depends(catalog_dependency)):
    return CareerResponse.model_validate(catalog.detail(id))
