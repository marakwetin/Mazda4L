from fastapi.templating import Jinja2Templates

from services.showroom import TEMPLATES_DIR


templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
