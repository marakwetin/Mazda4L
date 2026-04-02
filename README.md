# Mazda4L

Luxury Mazda inventory showroom built with FastAPI, Jinja2, Tailwind CSS, and Alpine.js.

The project includes:
- a filtered inventory homepage
- dedicated vehicle detail pages with gallery and finance estimator
- a build/configurator page for selected Mazda models
- a comparison engine
- an admin dashboard for creating, editing, deleting, and uploading cars
- multi-image uploads with empty-state handling when a car has no gallery

## Run

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

Routes:
- Inventory: `http://127.0.0.1:8000/`
- Vehicle Detail Page example: `http://127.0.0.1:8000/inventory/mazda-cx-60`
- Configurator example: `http://127.0.0.1:8000/build/mazda-cx-60`
- Admin dashboard: `http://127.0.0.1:8000/admin`
