import contextlib
import os
from typing import AsyncIterator, TypedDict

import anyio
import discord
import httpx
from anyio.abc import TaskGroup
from starlette.applications import Starlette

from .bot import Bot
from .routes import ROUTES


class State(TypedDict):
    bot: Bot
    http_client: httpx.AsyncClient
    task_group: TaskGroup


@contextlib.asynccontextmanager
async def lifespan(app) -> AsyncIterator[State]:
    discord.utils.setup_logging()

    bot = Bot()
    async with (
        anyio.create_task_group() as tg,
        httpx.AsyncClient() as http_client,
        bot,
    ):
        tg.start_soon(bot.start, os.environ.pop("BOT_TOKEN"))
        yield {"bot": bot, "http_client": http_client, "task_group": tg}


app = Starlette(
    debug=True,
    routes=ROUTES,
    lifespan=lifespan,
)
