from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from routes.common import templates
from services.showroom import inventory_context


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def inventory_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="inventory.html",
        context=inventory_context(request),
    )
