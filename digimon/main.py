from fastapi import FastAPI
from routes import init_routers
from models import init_db

app = FastAPI()

init_routers(app)
init_db()