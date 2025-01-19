from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot as AioBot
from environs import Env


@dataclass
class Bot:
    bot: AioBot
    admin_id: int
    admin_username: str


@dataclass
class Database:
    engine: str
    user: str
    pswd: str
    mame: str
    host: str
    echo: bool
    link: str = None


@dataclass
class Config:
    bot: Bot
    database: Database


def get_settings():
    env_var = Env()
    env_var.read_env()

    return Config(
        bot=Bot(
            bot=AioBot(env_var.str("TOKEN")),
            admin_id=env_var.int("ADMIN_ID"),
            admin_username=env_var.str("ADMIN_USERNAME"),
        ),
        database=Database(
            engine=env_var.str("DB_ENGINE"),
            user=env_var.str("DB_USER"),
            pswd=env_var.str("DB_PSWD"),
            mame=env_var.str("DB_DB"),
            host=env_var.str("DB_HOST"),
            echo=env_var.bool("DB_ECHO"),
        ),
    )


settings = get_settings()
sdb = settings.database
settings.database.link = f"{sdb.engine}://{sdb.user}:{sdb.pswd}@{sdb.host}/{sdb.mame}"
