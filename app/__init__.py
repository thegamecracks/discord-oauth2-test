import contextlib
import os

import anyio
import discord
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from .bot import Bot


@contextlib.asynccontextmanager
async def lifespan(app):
    discord.utils.setup_logging()

    bot = Bot()
    async with anyio.create_task_group() as tg, bot:
        tg.start_soon(bot.start, os.environ.pop("BOT_TOKEN"))
        yield


async def homepage(request):
    return JSONResponse({"hello": "world"})


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
    ],
    lifespan=lifespan,
)
