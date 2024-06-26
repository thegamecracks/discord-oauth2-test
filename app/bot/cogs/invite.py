from discord.ext import commands

from app.bot import Bot, Context
from app.routes.auth import auth_flow


class Invite(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def invite(self, ctx: Context) -> None:
        url = auth_flow.create_oauth_url(tg=self.bot.tg)
        await ctx.reply(url, delete_after=60)


async def setup(bot: Bot):
    await bot.add_cog(Invite(bot))
