import os
import sys
import traceback

from os.path import dirname, join, abspath, isfile, isdir
from os import listdir

from discord import VoiceState, Member, AuditLogAction, Intents
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Add common folder for execution
if isdir("common"):
    sys.path.append(abspath(join(dirname(__file__), "../")))

# pylint: disable=wrong-import-position
from common.bot_logger import get_logger, configure_logging

# pylint: enable=wrong-import-position

configure_logging("bot.log")

COGS_MODULE = "cogs"

TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX")

intents = Intents(messages=True, guilds=True, voice_states=True, members=True)
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
logger = get_logger(__name__)

if __name__ == "__main__":
    cogs_dir = join(dirname(__file__), "cogs")
    for extension in [
        f.replace(".py", "") for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))
    ]:
        # noinspection PyBroadException
        try:
            bot.load_extension(f"{COGS_MODULE}.{extension}")
        except Exception as e:
            print(
                f"Failed to load extension {COGS_MODULE}.{extension}.", file=sys.stderr
            )
            traceback.print_exc()


@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} has connected to Discord!")
    # update barfjes.


@bot.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    async for entry in member.guild.audit_logs(
        limit=1, action=AuditLogAction.member_update
    ):
        if entry.user == bot.user or entry.user.id == member.id:
            return
        if after.mute and not before.mute and member.guild_permissions.administrator:
            await member.edit(mute=False)
            await member.guild.get_member(entry.user.id).edit(mute=True)


# noinspection PyUnusedLocal
@bot.event
async def on_error(event_name):
    # pylint: disable=unused-argument
    logger.warning("Ignoring exception: %s", traceback.format_exc())
    # pylint: enable=unused-argument


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, "on_error"):
        return

    # This prevents any cogs with an overwritten cog_command_error being handled here.
    cog = ctx.cog
    if cog:
        # pylint: disable=protected-access
        # noinspection PyProtectedMember
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return
        # pylint: enable=protected-access

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, "original", error)

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That command does not exist.")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(f"{ctx.command} has been disabled.")
    else:
        logger.warning(
            "Ignoring exception in command %s:\n%s",
            ctx.command,
            "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            ),
        )


bot.run(TOKEN)
logger.warning("Bot stopped running")
