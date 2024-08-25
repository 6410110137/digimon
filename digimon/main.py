from fastapi import FastAPI
from . import routes
from . import models
from .models import init_db
from . import config

def create_app(settings=None):
    if not settings:
        settings = config.get_settings()
    app = FastAPI()

    models.init_db(settings)

    routes.init_routers(app)

    return app