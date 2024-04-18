import contextlib
import os
from typing import AsyncIterator, TypedDict

import anyio
import asyncpg
import discord
import httpx
from anyio.abc import TaskGroup
from starlette.applications import Starlette

from .bot import Bot
from .database import run_migrations
from .routes import ROUTES


class State(TypedDict):
    bot: Bot
    http_client: httpx.AsyncClient
    pool: asyncpg.Pool
    task_group: TaskGroup


@contextlib.asynccontextmanager
async def lifespan(app) -> AsyncIterator[State]:
    discord.utils.setup_logging()

    bot = Bot()
    pg_password = os.environ.pop("POSTGRES_PASSWORD")

    async with (
        anyio.create_task_group() as tg,
        httpx.AsyncClient() as http_client,
        asyncpg.create_pool("postgres://postgres@db", password=pg_password) as pool,
        bot,
    ):
        async with pool.acquire() as conn, conn.transaction():
            await run_migrations(conn)  # type: ignore

        tg.start_soon(bot.start, os.environ.pop("BOT_TOKEN"))
        yield {"bot": bot, "http_client": http_client, "pool": pool, "task_group": tg}


app = Starlette(
    debug=True,
    routes=ROUTES,
    lifespan=lifespan,
)
