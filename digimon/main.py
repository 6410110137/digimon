from fastapi import FastAPI
from . import routes
from . import models
from . import config

def create_app():
    settings = config.get_settings()
    app = FastAPI()

    models.init_db(settings)

    routes.init_router(app)

    @app.on_event("startup")
    async def on_startup():
        await models.create_all()

    return app