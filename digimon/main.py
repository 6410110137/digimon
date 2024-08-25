from gevent import monkey
from requests import session

monkey.patch_all()

from fastapi import FastAPI

from .models import init_db
from .routes import init_routers
from digimon import config

from contextlib import asynccontextmanager

from . import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if models.engine is not None:
        # Close the DB connection
        await session.close()


def create_app(settings=None):
    if not settings:
        settings = config.get_settings()

    app = FastAPI(lifespan=lifespan)

    init_db(settings)

    init_routers(app)
    return app