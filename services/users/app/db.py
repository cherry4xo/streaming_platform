import os
import uuid
import logging

from tortoise.contrib.fastapi import register_tortoise
from aerich import Command
from fastapi import FastAPI

from app import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_tortoise_config() -> dict:
    app_list = ["app.models", "aerich.models"]
    config = {
        "connections": settings.DB_CONNECTIONS,
        "apps": {
            "models": app_list,
            "default_connection": "default"
        }
    }
    return config

TORTOISE_ORM = get_tortoise_config()

def register_db(app: FastAPI, db_url: str = None) -> None:
    db_url = db_url or settings.DB_URL
    app_list = ["app.models", "aerich.models"]
    register_tortoise(
        app, 
        db_url=db_url,
        modules={"models": app_list},
        generate_schemas=True,
        add_exception_handlers=True
    )

async def upgrade_db() -> None:
    command = Command(tortoise_config=TORTOISE_ORM, app="models", location="./migrations")
    if not os.path.exists("./migrations/models"):
        await command.init_db(safe=True)
    await command.init()
    await command.migrate("update")
    await command.upgrade(run_in_transaction=True)


async def init_db(app: FastAPI) -> None:
    # await upgrade_db()
    register_db(app)
    logger.debug("Connected to db")