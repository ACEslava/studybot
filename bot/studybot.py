import asyncio
import logging
import os
import sys
import time
import traceback
from logging.handlers import TimedRotatingFileHandler

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
from functions.loading_message import get_loading_message

initial_cogs = ("cogs.utilities", "cogs.searchengines", "cogs.onhandling", "cogs.fun")
default_command_prefix = "&"

load_dotenv()
bot_owner = int(os.getenv("OWNER_ID"))
application_id = (
    os.getenv("APPLICATION_ID_DEV")
    if os.getenv("DEBUG_MODE") == "true"
    else os.getenv("APPLICATION_ID")
)
logging_channel_id = int(os.getenv("LOG_CHANNEL_ID"))


class UserError(Exception):
    """Exception for user-caused errors in the bot

    Parameters
    ----------
    reason : str
        Reasoning for why error occured
    """

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(self.reason)


class UserCancel(KeyboardInterrupt):
    """Raised when user cancels their command"""

    pass


class StudyBot(commands.Bot):
    """Class for the SearchIO Bot

    Attributes
    ----------
    owner_id : int
        Discord ID of the bot owner

    application_id : str
        Discord app ID of the bot

    loading_message : () -> str
        Function that gives a randomised loading msg

    session : aiohttp.ClientSession
        Pregenerated aiohttp ClientSession

    UserError : studybot.UserError
        Custom exception for user-attributed error

    UserCancel : studybot.UserCancel
        Raised when user cancels their command
    """

    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=default_command_prefix,
            intents=intents,
            owner_id=bot_owner,
            application_id=application_id,
        )

        # Set standard errors
        self.UserError = UserError
        self.UserCancel = UserCancel

        # Initialise loading message function
        self.loading_message = get_loading_message

        # Set up logging
        fmt = logging.Formatter("%(asctime)s %(name)s [%(levelname)s]: %(message)s")

        std = logging.StreamHandler(sys.stdout)
        std.setLevel(
            logging.DEBUG if os.getenv("DEBUG_MODE") == "true" else logging.INFO
        )
        std.setFormatter(fmt)

        rot = TimedRotatingFileHandler(
            filename="runtime.log",
            when="D",
            utc=True,
            interval=7,
            backupCount=4,
            encoding="utf-8",
            delay=False,
        )
        rot.setLevel(logging.INFO)
        rot.setFormatter(fmt)

        err = logging.FileHandler(filename="error.log", encoding="utf-8")
        err.setLevel(logging.ERROR)
        err.setFormatter(fmt)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(rot)
        self.logger.addHandler(std)
        self.logger.addHandler(err)

        # Sync check for slash commands
        self.isSynced = False

    async def setup_hook(self) -> None:
        # Load cogs
        for cog in initial_cogs:
            t0 = time.time()
            await self.load_extension(cog)
            t1 = time.time()
            self.logger.debug(f"{cog} loaded in {round(t1-t0, 5)} sec")

        # Initialise persistent ClientSession
        t0 = time.time()
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(keepalive_timeout=360.0, limit=None)
        )
        await (await self.session.get("https://www.google.com")).text()
        t1 = time.time()
        self.logger.debug(f"aiohttp session loaded in {round(t1-t0, 5)} sec")

    async def on_ready(self) -> None:
        # Set presence
        game = discord.Game("with your mom")
        await self.change_presence(status=discord.Status.idle, activity=game)
        self.logger.debug("Changing discord status")

        # Sync commands
        if not self.isSynced:
            tree_cmds = [c.name for c in self.tree.get_commands()]
            for cmd in await self.tree.fetch_commands():
                if cmd.name not in tree_cmds:
                    await cmd.delete()
            if os.getenv("DEBUG_MODE") == "true":
                self.tree.copy_global_to(guild=discord.Object(id=801170004179157033))
                await self.tree.sync(guild=discord.Object(id=801170004179157033))
            else:
                await self.tree.sync()

            self.logger.debug("Syncing slash commands")

        # Set logging channel
        self.logging_channel = self.get_channel(logging_channel_id)

        # Log ready event
        self.logger.info("-" * 15)
        self.logger.info("Bot successfully loaded")
        return

    async def on_command_error(self, ctx: commands.Context, e: Exception) -> None:
        # If user made an error in their command
        if isinstance(e, UserError):
            await ctx.send(embed=discord.Embed(description=e.reason))
            return

        # If certain errors are raised, ignore it
        elif isinstance(e, (asyncio.TimeoutError, commands.errors.CommandNotFound)):
            return

        # Cooldown
        elif isinstance(e, commands.errors.CommandOnCooldown):
            await ctx.send(
                embed=discord.Embed(
                    description="Command on cooldown. Wait "
                    + f"{round(e.retry_after, 2)} sec"
                )
            )
            self.logger.info("Command ratelimited")
            return
        self.logger.error(e, exc_info=True)

        if ctx.author.id == self.owner_id:
            await ctx.send(f"```{e}{chr(10)}{traceback.format_exc()}```")
        else:
            err_embed = discord.Embed(
                title=":(",
                description=(
                    "An unknown error has occurred,"
                    + " please try a different command."
                ),
            )
            await ctx.send(embed=err_embed)
            return

    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.logger.info(f"Bot joined guild {guild.name}")
        return

    async def on_guild_leave(self) -> None:
        return
