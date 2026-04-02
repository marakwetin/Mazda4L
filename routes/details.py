from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from routes.common import templates
from services.showroom import vehicle_context


router = APIRouter(prefix="/inventory")


@router.get("/{car_id}", response_class=HTMLResponse)
async def vehicle_detail_page(request: Request, car_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="vdp.html",
        context=vehicle_context(request, car_id),
    )
