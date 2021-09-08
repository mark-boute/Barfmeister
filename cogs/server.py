import asyncio

import discord
from discord.ext import commands, tasks

from common.bot_logger import get_logger
from common.bois_functions import reply_and_delete
from common.server_functions import (
    get_by_status,
    get_configs,
    add_config,
    remove_config,
    find_dir,
    check_config_availability,
)

logger = get_logger(__name__)


class ServerCog(commands.Cog, name="Server command"):
    def __init__(self, bot):
        self.bot = bot
        # should have guild specific files if used in more guilds
        self.status_lock = asyncio.Lock()
        self.config_lock = asyncio.Lock()
        logger.info("Server cog initialized")

    @commands.group(
        name="server",
        invoke_without_command=True,
        help="Manage Servers",
    )
    async def server(self, ctx):
        await ctx.reply("No subcommand was found!")
        await ctx.send_help(self.server)

    @server.command(help="Start server [server]")
    @commands.has_role("Boi")
    async def start(self, ctx, *args):
        # check if running
        # add running status
        # start server
        # checks

        pass

    @server.command(help="Shutdown server [server]")
    @commands.has_role("Boi")
    async def shutdown(self, ctx, *args):
        # check if running
        # rem running status
        # shutdown server
        # checks

        pass

    @server.command(help="Get server status for server [name]")
    async def status(self, ctx, name):

        # get server dir
        # return status from script

        pass

    @server.group(name="list", invoke_without_command=True, help="List servers")
    async def list(self, ctx):
        print(get_by_status(self.status_lock, running=True))
        print(get_by_status(self.status_lock, running=False))

    @list.command(help="List running servers")
    async def running(self, ctx):
        print(get_by_status(self.status_lock, running=True))

    @list.command(help="List non-running servers")
    async def off(self, ctx):
        print(get_by_status(self.status_lock, running=False))

    @server.group(
        name="config", invoke_without_command=True, help="Manage server configurations"
    )
    @commands.has_role("Boi")
    async def config(self, ctx):
        await ctx.reply("No subcommand was found!")
        await ctx.send_help(self.server)

    @config.command(help="Create new server config [name] [dir]")
    @commands.has_role("Boi")
    async def create(self, ctx, *args):
        server_dir = args[-1]
        name = " ".join(word for word in args[:-1])

        configs = await get_configs(self.config_lock)
        if not await check_config_availability(ctx, configs, name, server_dir):
            return

        if find_dir(server_dir):
            configs.append((name, server_dir))
            if await add_config(self.config_lock, name, server_dir):
                await reply_and_delete(
                    ctx, f"Successfully added server {name} with dir {server_dir}."
                )
            else:
                await reply_and_delete(
                    ctx, "Something went wrong, name or dir already in file."
                )
        else:
            await reply_and_delete(
                ctx, "This directory does not exist or is missing files."
            )

    @config.command(help="Remove server config [name]")
    @commands.has_role("Boi")
    async def remove(self, ctx, name):
        await remove_config(self.config_lock, name)
        await reply_and_delete(
            ctx, f"If {name} was in the config file, it has been removed."
        )

    @config.command(help="Edit server config [name] [new dir]")
    @commands.has_role("Boi")
    async def edit(self, ctx, *args):
        server_dir = args[-1]
        name = " ".join(word for word in args[:-1])

        if not find_dir(server_dir):
            await reply_and_delete(
                ctx, "This directory does not exist or is missing files."
            )
            return

        configs = await get_configs(self.config_lock)
        if not await check_config_availability(ctx, configs, name, server_dir):
            return

        # warning: this is really ugly and bad performing code,
        # as it acquires the lock 3 times instead of just once.
        if len(configs) == len(await remove_config(self.config_lock, name)):
            await add_config(self.config_lock, name, server_dir)
            await reply_and_delete(ctx, f"Server {name} now has dir {server_dir}.")
        else:
            await reply_and_delete(ctx, f"Config {name} does not exist.")

    async def _server_manager(self):
        # updates status
        # return list of servers it shut down
        return []

    @tasks.loop(minutes=10)
    async def auto_server_manager(self):
        logger.info("Running periodic server manager")
        for name, _ in await self._server_manager():
            logger.info(f"Shutdown {name}")
        logger.info("Server manager complete")

    @auto_server_manager.before_loop
    async def before_auto_server_manager(self):
        await self.bot.wait_until_ready()

    @commands.has_role("Boi")
    @server.command(help="Run server manager")
    async def manage(self, ctx):
        shutdown = await self._server_manager()
        if shutdown:
            embed = discord.Embed(title="Servers shutdown:", color=0x4E06D2)
            for name, _ in shutdown:
                embed.add_field(name="\u200b", value=name)
            await ctx.channel.send(embed=embed)
            await ctx.message.delete()
        else:
            await reply_and_delete(ctx, "No servers were shutdown")


def setup(bot):
    bot.add_cog(ServerCog(bot))
