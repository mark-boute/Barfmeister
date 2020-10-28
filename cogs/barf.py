import discord
from discord.ext import commands
from common.bot_logger import get_logger
from common.helper_functions import add_barf, rem_barf, update_barfjes


logger = get_logger(__name__)


class BarfCog(commands.Cog, name="Barf commands"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Barf cog initialized")

    @commands.group(
        name="barf", invoke_without_command=True, help="Get help for barf commands"
    )
    async def barf(self, ctx):
        await ctx.send("'barf' needs a sub-command!")
        await ctx.send_help(self.barf)

    @barf.command(
        help="Someone barfed, add it to their score using this command:"
        ' !barf add [name] ["story"] [optional: date, using DD-MM-YYYY (default: current date)]'
    )
    async def add(self, ctx, user: discord.Member, reason: str, date: str = None):

        barf_count = add_barf(ctx, user, reason, date)

        if not barf_count:
            return

        await update_barfjes()
        await ctx.channel.send(
            f"Barf added, {user.display_name} barfed {barf_count} times!"
        )
        ctx.message.delete()

    @barf.command(
        help="remove a barf from the scoreboard using: !barf rem [name] [date]"
    )
    @commands.has_role("Boi")
    async def rem(self, ctx, user: discord.Member, date: str = None):

        barf_info = rem_barf(ctx, user, date)

        if not barf_info:
            return

        await update_barfjes()
        await ctx.channel.send(barf_info)
        ctx.message.delete()


def setup(bot):
    bot.add_cog(BarfCog(bot))
