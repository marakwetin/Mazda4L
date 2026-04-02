from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.admin import router as admin_router
from routes.configurator import router as configurator_router
from routes.details import router as details_router
from routes.inventory import router as inventory_router
from services.showroom import STATIC_DIR, ensure_data_files


ensure_data_files()

app = FastAPI(
    title="AutoElite Mazda",
    description="Luxury Mazda inventory, vehicle detail pages, build configurators, and admin management.",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(inventory_router)
app.include_router(details_router)
app.include_router(configurator_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event() -> None:
    ensure_data_files()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
