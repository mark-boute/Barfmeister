import datetime
import discord
from common.bot_logger import get_logger

logger = get_logger(__name__)
now = datetime.datetime.now()


async def reply_and_delete(ctx, reply: str):
    try:
        await ctx.author.send(reply)
        await ctx.message.delete()
    except:
        if ctx.guild:
            logger.warning(
                "Could not reply to/remove old message: 'ctx.message.content=%s' by user: 'ctx.author=%s'",
                ctx.message.content,
                ctx.author,
            )


async def get_date_string_from_user(ctx, date: str = None):
    if not date:
        date = f"{now.day}-{now.month}-{now.year}"
    else:
        try:
            d = datetime.datetime.strptime(date, "%d-%m-%Y")
            date = f"{d.day}-{d.month}-{d.year}"
        except ValueError:
            await reply_and_delete(
                ctx,
                "Not the correct format for date! You should use: DD-MM-YYYY. For instance 14-01-2020",
            )
            return False
    return date


async def get_date_from_string(date: str):
    try:
        d = datetime.datetime.strptime(date, "%d-%m-%Y")
    except:
        pass


# -------------- Barf Cog functions --------------


async def add_barf(ctx, user: discord.Member, reason: str, date: str = None):
    date = get_date_string_from_user(ctx, date)

    # #barfjes


async def rem_barf(ctx, user: discord.Member, date: str = None):
    date = get_date_string_from_user(ctx, date)

    # user reason date
    # f'Removed barf "{barf_text}" with date {barf_date} from {barf_user}'


async def update_barfjes():
    pass
