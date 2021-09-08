import discord
from discord.ext import commands
from common.bot_logger import get_logger
from common.bois_functions import (
    add_barf,
    rem_barf,
    update_barfjes,
    reply_and_delete,
    get_boi_barf_info,
)

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

        barf_count = add_barf(user, reason, date)
        if barf_count == -1:
            await reply_and_delete(
                ctx,
                "Not the correct date format! You should use: DD-MM-YYYY. For instance 14-01-2020",
            )
            return
        if barf_count == -2:
            await reply_and_delete(
                ctx,
                "Only one barf per day allowed",
            )
            return

        await update_barfjes(self.bot.get_channel(722112470969221281))
        await ctx.channel.send(
            f"Barf added, {user.display_name} barfed {barf_count} times!"
        )
        await ctx.message.delete()

    @barf.command(
        help="remove a barf from the scoreboard using: !barf rem [name] [date]"
    )
    @commands.has_role("Boi")
    async def rem(self, ctx, user: discord.Member, date: str = None):

        barf_info = rem_barf(user, date)

        if not barf_info:
            return

        await update_barfjes(self.bot.get_channel(722112470969221281))
        await ctx.channel.send(barf_info)
        await ctx.message.delete()

    @barf.command(help="testing")
    @commands.has_role("Boi")
    async def update(self, ctx):
        await update_barfjes(ctx, self.bot.get_channel(722112470969221281))
        await ctx.message.delete()

    @barf.command(
        help="get a boi's barfjes from a specified year !barf info [boi] [year]"
    )
    async def info(self, ctx, member: discord.Member, year: int):
        await get_boi_barf_info(ctx, member, year)


def setup(bot):
    bot.add_cog(BarfCog(bot))
