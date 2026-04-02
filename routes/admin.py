from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from routes.common import templates
from services.showroom import admin_context, load_inventory, remove_unused_uploads, save_inventory, upsert_car


router = APIRouter(prefix="/admin")


@router.get("", response_class=HTMLResponse)
async def admin_page(request: Request, message: str | None = None, error: str | None = None) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context=admin_context(request, message=message, error=error),
    )


@router.post("/cars/create")
async def create_car(
    model_name: str = Form(...),
    year: int = Form(...),
    engine_type: str = Form(...),
    mileage_km: int = Form(...),
    exterior_color: str = Form(...),
    body_style: str = Form(...),
    transmission: str = Form(...),
    base_price: int = Form(...),
    availability: str = Form(...),
    headline: str = Form(...),
    summary: str = Form(...),
    horsepower: int = Form(...),
    torque_nm: int = Form(...),
    zero_to_hundred_s: float = Form(...),
    drivetrain: str = Form(...),
    range_estimate: str = Form(...),
    seats: int = Form(...),
    featured: str | None = Form(None),
    certified_provenance: str | None = Form(None),
    clear_gallery: str | None = Form(None),
    images: list[UploadFile] | None = File(None),
) -> RedirectResponse:
    inventory = load_inventory()
    try:
        await upsert_car(
            inventory,
            model_name=model_name,
            year=year,
            engine_type=engine_type,
            mileage_km=mileage_km,
            exterior_color=exterior_color,
            body_style=body_style,
            transmission=transmission,
            base_price=base_price,
            availability=availability,
            headline=headline,
            summary=summary,
            horsepower=horsepower,
            torque_nm=torque_nm,
            zero_to_hundred_s=zero_to_hundred_s,
            drivetrain=drivetrain,
            range_estimate=range_estimate,
            seats=seats,
            certified_provenance=certified_provenance == "on",
            featured=featured == "on",
            images=images,
            clear_gallery=clear_gallery == "on",
        )
    except HTTPException as exc:
        return RedirectResponse(url=f"/admin?error={quote(str(exc.detail))}", status_code=303)

    return RedirectResponse(url=f"/admin?message={quote('Car created')}", status_code=303)


@router.post("/cars/{car_id}/update")
async def update_car(
    car_id: str,
    model_name: str = Form(...),
    year: int = Form(...),
    engine_type: str = Form(...),
    mileage_km: int = Form(...),
    exterior_color: str = Form(...),
    body_style: str = Form(...),
    transmission: str = Form(...),
    base_price: int = Form(...),
    availability: str = Form(...),
    headline: str = Form(...),
    summary: str = Form(...),
    horsepower: int = Form(...),
    torque_nm: int = Form(...),
    zero_to_hundred_s: float = Form(...),
    drivetrain: str = Form(...),
    range_estimate: str = Form(...),
    seats: int = Form(...),
    featured: str | None = Form(None),
    certified_provenance: str | None = Form(None),
    clear_gallery: str | None = Form(None),
    images: list[UploadFile] | None = File(None),
) -> RedirectResponse:
    inventory = load_inventory()
    try:
        await upsert_car(
            inventory,
            model_name=model_name,
            year=year,
            engine_type=engine_type,
            mileage_km=mileage_km,
            exterior_color=exterior_color,
            body_style=body_style,
            transmission=transmission,
            base_price=base_price,
            availability=availability,
            headline=headline,
            summary=summary,
            horsepower=horsepower,
            torque_nm=torque_nm,
            zero_to_hundred_s=zero_to_hundred_s,
            drivetrain=drivetrain,
            range_estimate=range_estimate,
            seats=seats,
            certified_provenance=certified_provenance == "on",
            featured=featured == "on",
            images=images,
            clear_gallery=clear_gallery == "on",
            existing_id=car_id,
        )
    except HTTPException as exc:
        return RedirectResponse(url=f"/admin?error={quote(str(exc.detail))}", status_code=303)

    return RedirectResponse(url=f"/admin?message={quote('Car updated')}", status_code=303)


@router.post("/cars/{car_id}/delete")
async def delete_car(car_id: str) -> RedirectResponse:
    inventory = load_inventory()
    cars = inventory.get("cars", [])
    if len(cars) <= 1:
        return RedirectResponse(url=f"/admin?error={quote('At least one car must remain')}", status_code=303)

    inventory["cars"] = [car for car in cars if car["id"] != car_id]
    if not any(car.get("featured") for car in inventory["cars"]):
        inventory["cars"][0]["featured"] = True
    save_inventory(inventory)
    remove_unused_uploads(inventory["cars"])
    return RedirectResponse(url=f"/admin?message={quote('Car deleted')}", status_code=303)
