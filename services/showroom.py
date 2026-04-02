from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request, UploadFile


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = STATIC_DIR / "uploads"
INVENTORY_PATH = DATA_DIR / "showroom.json"
WHEEL_OPTIONS = [
    {
        "id": "pure-white",
        "name": '20" Forged Pure White',
        "finish": "Pure White",
        "price_delta": 280000,
        "description": "Clean forged finish with a brighter contrast against Deep Ink bodywork.",
        "image": "/static/images/wheel-white.svg",
    },
    {
        "id": "blood-red",
        "name": '20" Blood Red',
        "finish": "Blood Red",
        "price_delta": 320000,
        "description": "Soul Red-inspired finish with a stronger visual hit under direct light.",
        "image": "/static/images/wheel-red.svg",
    },
]


def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    if not INVENTORY_PATH.exists():
        INVENTORY_PATH.write_text(json.dumps({"cars": []}, indent=2), encoding="utf-8")


def format_currency(amount: int | float) -> str:
    return f"KSh {amount:,.0f}"


def _normalize_specs(raw_specs: dict[str, Any] | None) -> dict[str, Any]:
    specs = raw_specs or {}
    return {
        "horsepower": int(specs.get("horsepower", 0)),
        "torque_nm": int(specs.get("torque_nm", 0)),
        "zero_to_hundred_s": round(float(specs.get("zero_to_hundred_s", 0)), 1),
        "drivetrain": str(specs.get("drivetrain", "AWD")),
        "range_estimate": str(specs.get("range_estimate", "N/A")),
        "seats": int(specs.get("seats", 5)),
    }


def _normalize_variant(raw_variant: dict[str, Any], *, fallback_specs: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(raw_variant.get("id") or safe_slug(str(raw_variant.get("name") or "variant"))),
        "name": str(raw_variant.get("name") or "Configured Variant"),
        "engine_type": str(raw_variant.get("engine_type") or raw_variant.get("powertrain") or "Mazda Powertrain"),
        "fuel": str(raw_variant.get("fuel") or "Hybrid"),
        "horsepower": int(raw_variant.get("horsepower", fallback_specs["horsepower"])),
        "torque_nm": int(raw_variant.get("torque_nm", fallback_specs["torque_nm"])),
        "zero_to_hundred_s": round(float(raw_variant.get("zero_to_hundred_s", fallback_specs["zero_to_hundred_s"])), 1),
        "range_estimate": str(raw_variant.get("range_estimate", fallback_specs["range_estimate"])),
        "drivetrain": str(raw_variant.get("drivetrain", fallback_specs["drivetrain"])),
        "price_delta": int(raw_variant.get("price_delta", 0)),
        "summary": str(raw_variant.get("summary") or "Balanced performance with a Mazda-first calibration."),
    }


def default_configurator_variants(car: dict[str, Any]) -> list[dict[str, Any]]:
    specs = car["specs"]
    model_name = car["model_name"]
    if "CX-60" in model_name or "CX-90" in model_name:
        return [
            {
                "id": "inline6-gas",
                "name": "3.3L Turbo Inline-6",
                "engine_type": "e-Skyactiv G",
                "fuel": "Gasoline",
                "horsepower": max(specs["horsepower"], 280),
                "torque_nm": max(specs["torque_nm"] - 40, 450),
                "zero_to_hundred_s": min(max(specs["zero_to_hundred_s"] - 0.3, 5.8), 7.2),
                "range_estimate": "760 km est.",
                "drivetrain": "AWD",
                "price_delta": 0,
                "summary": "The cleanest balance of straight-six presence, torque delivery, and quiet touring manners.",
            },
            {
                "id": "turbo-diesel",
                "name": "3.3L Turbo Diesel",
                "engine_type": "e-Skyactiv D",
                "fuel": "Diesel",
                "horsepower": max(specs["horsepower"] - 24, 254),
                "torque_nm": max(specs["torque_nm"], 550),
                "zero_to_hundred_s": max(specs["zero_to_hundred_s"], 7.4),
                "range_estimate": "980 km est.",
                "drivetrain": "AWD",
                "price_delta": 170000,
                "summary": "Long-range torque and low-effort highway speed tuned for Kenya's distance-heavy driving.",
            },
            {
                "id": "phev",
                "name": "2.5L PHEV",
                "engine_type": "e-Skyactiv PHEV",
                "fuel": "PHEV",
                "horsepower": max(specs["horsepower"], 323),
                "torque_nm": max(specs["torque_nm"], 500),
                "zero_to_hundred_s": min(specs["zero_to_hundred_s"], 6.4),
                "range_estimate": "42 km EV / 760 km combined",
                "drivetrain": "AWD",
                "price_delta": 260000,
                "summary": "The sharpest launch and the quietest low-speed character in the CX family configuration lane.",
            },
        ]
    if "MX-5" in model_name:
        return [
            {
                "id": "roadster-manual",
                "name": "2.0 Roadster Manual",
                "engine_type": "Skyactiv-G 2.0",
                "fuel": "Gasoline",
                "horsepower": 181,
                "torque_nm": 205,
                "zero_to_hundred_s": 6.7,
                "range_estimate": "610 km est.",
                "drivetrain": "RWD",
                "price_delta": 0,
                "summary": "The lightest-feeling spec with the most direct driver feedback.",
            },
            {
                "id": "rf-grand-touring",
                "name": "RF Grand Touring",
                "engine_type": "Skyactiv-G 2.0",
                "fuel": "Gasoline",
                "horsepower": 184,
                "torque_nm": 208,
                "zero_to_hundred_s": 6.5,
                "range_estimate": "600 km est.",
                "drivetrain": "RWD",
                "price_delta": 210000,
                "summary": "A tighter, more refined roofline with grand-tourer polish over the standard roadster.",
            },
            {
                "id": "club-track",
                "name": "Club Track Pack",
                "engine_type": "Skyactiv-G 2.0",
                "fuel": "Gasoline",
                "horsepower": 184,
                "torque_nm": 210,
                "zero_to_hundred_s": 6.3,
                "range_estimate": "590 km est.",
                "drivetrain": "RWD",
                "price_delta": 320000,
                "summary": "The most aggressive suspension and wheel tuning in the MX-5 build stack.",
            },
        ]
    if "Mazda3" in model_name:
        return [
            {
                "id": "skyactiv-g",
                "name": "Skyactiv-G 2.0",
                "engine_type": "Skyactiv-G 2.0",
                "fuel": "Gasoline",
                "horsepower": 186,
                "torque_nm": 240,
                "zero_to_hundred_s": 8.1,
                "range_estimate": "670 km est.",
                "drivetrain": "FWD",
                "price_delta": 0,
                "summary": "The most straightforward sedan tune, balanced for daily use and premium restraint.",
            },
            {
                "id": "skyactiv-x",
                "name": "Skyactiv-X Mild Hybrid",
                "engine_type": "Skyactiv-X",
                "fuel": "Mild Hybrid",
                "horsepower": 190,
                "torque_nm": 240,
                "zero_to_hundred_s": 7.8,
                "range_estimate": "720 km est.",
                "drivetrain": "FWD",
                "price_delta": 190000,
                "summary": "Sharper combustion efficiency and a cleaner power delivery curve for city-to-coast runs.",
            },
            {
                "id": "turbo-awd",
                "name": "2.5 Turbo AWD",
                "engine_type": "Skyactiv-G Turbo",
                "fuel": "Gasoline",
                "horsepower": 250,
                "torque_nm": 434,
                "zero_to_hundred_s": 6.3,
                "range_estimate": "640 km est.",
                "drivetrain": "AWD",
                "price_delta": 360000,
                "summary": "The most muscular small-sedan spec in the configurator, tuned for speed with composure.",
            },
        ]
    return [
        {
            "id": "signature",
            "name": "Signature Trim",
            "engine_type": car["engine_type"],
            "fuel": "Mazda Premium",
            "horsepower": specs["horsepower"],
            "torque_nm": specs["torque_nm"],
            "zero_to_hundred_s": specs["zero_to_hundred_s"],
            "range_estimate": specs["range_estimate"],
            "drivetrain": specs["drivetrain"],
            "price_delta": 0,
            "summary": "A composed flagship trim with premium materials and restrained performance tuning.",
        }
    ]


def configurator_variants_for_car(car: dict[str, Any]) -> list[dict[str, Any]]:
    raw_variants = car.get("configurator_variants")
    if isinstance(raw_variants, list) and raw_variants:
        return [_normalize_variant(variant, fallback_specs=car["specs"]) for variant in raw_variants if isinstance(variant, dict)]
    return default_configurator_variants(car)


def normalize_car(raw_car: dict[str, Any]) -> dict[str, Any]:
    images = [str(url) for url in raw_car.get("images", []) if str(url).strip()]

    specs = _normalize_specs(raw_car.get("specs"))
    normalized = {
        **raw_car,
        "model_name": raw_car.get("model_name") or raw_car.get("name") or "Untitled Mazda",
        "headline": raw_car.get("headline") or raw_car.get("tagline") or "Curated performance inventory.",
        "summary": raw_car.get("summary") or raw_car.get("intro") or "",
        "year": int(raw_car.get("year", 2024)),
        "engine_type": raw_car.get("engine_type") or "Skyactiv-G",
        "mileage_km": int(raw_car.get("mileage_km", 0)),
        "exterior_color": raw_car.get("exterior_color") or "Soul Red Crystal",
        "body_style": raw_car.get("body_style") or "SUV",
        "transmission": raw_car.get("transmission") or "Automatic",
        "availability": raw_car.get("availability") or "Available",
        "base_price": int(raw_car.get("base_price", 0)),
        "certified_provenance": bool(raw_car.get("certified_provenance", False)),
        "featured": bool(raw_car.get("featured", False)),
        "images": images,
        "primary_image": images[0] if images else None,
        "image_count": len(images),
        "price_label": format_currency(int(raw_car.get("base_price", 0))),
        "specs": specs,
    }
    normalized["configurator_variants"] = configurator_variants_for_car(normalized)
    return normalized


def serialize_car(car: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "id": car["id"],
        "model_name": car["model_name"],
        "year": int(car["year"]),
        "engine_type": car["engine_type"],
        "mileage_km": int(car["mileage_km"]),
        "exterior_color": car["exterior_color"],
        "body_style": car["body_style"],
        "transmission": car["transmission"],
        "base_price": int(car["base_price"]),
        "availability": car["availability"],
        "headline": car["headline"],
        "summary": car["summary"],
        "certified_provenance": bool(car.get("certified_provenance", False)),
        "featured": bool(car.get("featured", False)),
        "images": [str(url) for url in car.get("images", []) if str(url).strip()],
        "specs": _normalize_specs(car.get("specs")),
    }
    variants = car.get("configurator_variants")
    if isinstance(variants, list) and variants:
        payload["configurator_variants"] = [
            _normalize_variant(variant, fallback_specs=payload["specs"])
            for variant in variants
            if isinstance(variant, dict)
        ]
    return payload


def load_inventory() -> dict[str, Any]:
    ensure_data_files()
    with INVENTORY_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    data["cars"] = [normalize_car(car) for car in data.get("cars", [])]
    return data


def save_inventory(inventory: dict[str, Any]) -> None:
    ensure_data_files()
    payload = {"cars": [serialize_car(car) for car in inventory.get("cars", [])]}
    INVENTORY_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def featured_car(cars: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not cars:
        return None
    return next((car for car in cars if car.get("featured")), cars[0])


def similar_cars(cars: list[dict[str, Any]], current_car_id: str) -> list[dict[str, Any]]:
    return [car for car in cars if car["id"] != current_car_id][:3]


def safe_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or f"mazda-{uuid.uuid4().hex[:8]}"


def unique_car_id(cars: list[dict[str, Any]], model_name: str, existing_id: str | None = None) -> str:
    base = safe_slug(model_name)
    used_ids = {car["id"] for car in cars if car["id"] != existing_id}
    candidate = base
    suffix = 2
    while candidate in used_ids:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def get_car_or_404(cars: list[dict[str, Any]], car_id: str) -> dict[str, Any]:
    car = next((item for item in cars if item["id"] == car_id), None)
    if car is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    return car


async def save_uploaded_images(images: list[UploadFile] | None) -> list[str]:
    if not images:
        return []

    saved_images: list[str] = []
    for image in images:
        if not image or not image.filename:
            continue
        suffix = Path(image.filename).suffix.lower() or ".bin"
        file_name = f"{uuid.uuid4().hex}{suffix}"
        target = UPLOADS_DIR / file_name
        with target.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        saved_images.append(f"/static/uploads/{file_name}")
    return saved_images


def remove_unused_uploads(cars: list[dict[str, Any]]) -> None:
    ensure_data_files()
    used_images = {url for car in cars for url in car.get("images", []) if url.startswith("/static/uploads/")}
    for file_path in UPLOADS_DIR.iterdir():
        public_path = f"/static/uploads/{file_path.name}"
        if public_path not in used_images and file_path.is_file():
            file_path.unlink()


def breadcrumbs_for(*items: tuple[str, str | None]) -> list[dict[str, Any]]:
    return [{"label": label, "href": href} for label, href in items]


def nav_context(cars: list[dict[str, Any]], *, page_kind: str, current_car: dict[str, Any] | None = None) -> dict[str, Any]:
    featured = featured_car(cars) or current_car
    custom_href = f"/build/{featured['id']}" if featured else "/"
    return {
        "page_kind": page_kind,
        "nav_links": {
            "inventory": "/",
            "customization_lab": custom_href,
            "contact": "#contact",
        },
    }


def inventory_context(request: Request, message: str | None = None) -> dict[str, Any]:
    inventory = load_inventory()
    cars = inventory["cars"]
    featured = featured_car(cars)
    years = sorted({car["year"] for car in cars}, reverse=True)
    body_styles = sorted({car["body_style"] for car in cars})
    transmissions = sorted({car["transmission"] for car in cars})
    return {
        "request": request,
        "cars": cars,
        "featured_car": featured,
        "filter_options": {
            "years": years,
            "body_styles": body_styles,
            "transmissions": transmissions,
        },
        "initial_query": request.query_params.get("q", ""),
        "message": message,
        "breadcrumbs": breadcrumbs_for(("Inventory", None)),
        **nav_context(cars, page_kind="inventory", current_car=featured),
    }


def vehicle_context(request: Request, car_id: str) -> dict[str, Any]:
    inventory = load_inventory()
    cars = inventory["cars"]
    car = get_car_or_404(cars, car_id)
    return {
        "request": request,
        "car": car,
        "related_cars": similar_cars(cars, car_id),
        "breadcrumbs": breadcrumbs_for(("Inventory", "/"), (car["model_name"], f"/inventory/{car_id}"), ("High Performance", None)),
        **nav_context(cars, page_kind="vdp", current_car=car),
    }


def configurator_context(request: Request, car_id: str) -> dict[str, Any]:
    inventory = load_inventory()
    cars = inventory["cars"]
    car = get_car_or_404(cars, car_id)
    variants = configurator_variants_for_car(car)
    return {
        "request": request,
        "car": car,
        "variants": variants,
        "wheel_options": WHEEL_OPTIONS,
        "breadcrumbs": breadcrumbs_for(("Inventory", "/"), (car["model_name"], f"/inventory/{car_id}"), ("Customization Lab", None)),
        **nav_context(cars, page_kind="configurator", current_car=car),
    }


def admin_context(request: Request, message: str | None = None, error: str | None = None) -> dict[str, Any]:
    inventory = load_inventory()
    return {
        "request": request,
        "cars": inventory["cars"],
        "message": message,
        "error": error,
        "breadcrumbs": breadcrumbs_for(("Inventory", "/"), ("Admin Studio", None)),
        **nav_context(inventory["cars"], page_kind="admin", current_car=featured_car(inventory["cars"])),
    }


async def upsert_car(
    inventory: dict[str, Any],
    *,
    model_name: str,
    year: int,
    engine_type: str,
    mileage_km: int,
    exterior_color: str,
    body_style: str,
    transmission: str,
    base_price: int,
    availability: str,
    headline: str,
    summary: str,
    horsepower: int,
    torque_nm: int,
    zero_to_hundred_s: float,
    drivetrain: str,
    range_estimate: str,
    seats: int,
    certified_provenance: bool,
    featured: bool,
    images: list[UploadFile] | None,
    clear_gallery: bool,
    existing_id: str | None = None,
) -> None:
    cars = inventory.get("cars", [])
    uploaded_images = await save_uploaded_images(images)
    car_id = unique_car_id(cars, model_name, existing_id=existing_id)

    if existing_id:
        car = next((item for item in cars if item["id"] == existing_id), None)
        if car is None:
            raise HTTPException(status_code=404, detail="Car not found.")
        current_images = car.get("images", [])
    else:
        car = None
        current_images = []

    if clear_gallery:
        final_images = uploaded_images
    elif uploaded_images:
        final_images = [*current_images, *uploaded_images]
    else:
        final_images = current_images

    payload = {
        **(car or {}),
        "id": car_id,
        "model_name": model_name.strip(),
        "year": int(year),
        "engine_type": engine_type.strip(),
        "mileage_km": int(mileage_km),
        "exterior_color": exterior_color.strip(),
        "body_style": body_style.strip(),
        "transmission": transmission.strip(),
        "base_price": int(base_price),
        "availability": availability.strip(),
        "headline": headline.strip(),
        "summary": summary.strip(),
        "certified_provenance": certified_provenance,
        "featured": featured,
        "images": final_images,
        "specs": _normalize_specs(
            {
                "horsepower": horsepower,
                "torque_nm": torque_nm,
                "zero_to_hundred_s": zero_to_hundred_s,
                "drivetrain": drivetrain,
                "range_estimate": range_estimate,
                "seats": seats,
            }
        ),
    }

    if car is None:
        cars.append(payload)
    else:
        car.update(payload)

    if featured and cars:
        for item in cars:
            item["featured"] = item["id"] == car_id
    elif cars and not any(item.get("featured") for item in cars):
        cars[0]["featured"] = True

    inventory["cars"] = [normalize_car(item) for item in cars]
    save_inventory(inventory)
    remove_unused_uploads(inventory["cars"])
