from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from routes.common import templates
from services.showroom import configurator_context


router = APIRouter(prefix="/build")


@router.get("/{model_id}", response_class=HTMLResponse)
async def configurator_page(request: Request, model_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="configurator.html",
        context=configurator_context(request, model_id),
    )
