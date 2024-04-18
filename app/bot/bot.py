import discord
from discord.ext import commands

EXTENSIONS = ()


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="?", intents=intents)

    async def setup_hook(self) -> None:
        for ext in EXTENSIONS:
            await self.load_extension(ext, package=__package__)