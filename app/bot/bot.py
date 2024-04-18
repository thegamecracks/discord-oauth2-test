import asyncpg
import discord
from anyio.abc import TaskGroup
from discord.ext import commands

EXTENSIONS = (
    ".cogs.invite",
)


class Bot(commands.Bot):
    def __init__(self, *, pool: asyncpg.Pool, tg: TaskGroup) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.pool = pool
        self.tg = tg

    async def setup_hook(self) -> None:
        for ext in EXTENSIONS:
            await self.load_extension(ext, package=__package__)


class Context(commands.Context[Bot]): ...
