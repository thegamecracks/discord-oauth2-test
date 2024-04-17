import contextlib
import os

import anyio
import discord
from starlette.applications import Starlette

from .bot import Bot
from .routes import ROUTES


@contextlib.asynccontextmanager
async def lifespan(app):
    discord.utils.setup_logging()

    bot = Bot()
    async with anyio.create_task_group() as tg, bot:
        tg.start_soon(bot.start, os.environ.pop("BOT_TOKEN"))
        yield


app = Starlette(
    debug=True,
    routes=ROUTES,
    lifespan=lifespan,
)
