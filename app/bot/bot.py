import asyncpg
import discord
from discord.ext import commands

EXTENSIONS = (
    ".cogs.invite",
)


class Bot(commands.Bot):
    def __init__(self, *, pool: asyncpg.Pool) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.pool = pool

    async def setup_hook(self) -> None:
        for ext in EXTENSIONS:
            await self.load_extension(ext, package=__package__)


class Context(commands.Context[Bot]): ...
