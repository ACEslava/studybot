import asyncio
import logging
import os
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
from functions.loading_message import get_loading_message

initial_cogs = ("cogs.utilities", "cogs.searchengines", "cogs.onhandling")
default_command_prefix = "&"

load_dotenv()
bot_owner = int(os.getenv("OWNER_ID"))
application_id = os.getenv("APPLICATION_ID")


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

    async def setup_hook(self) -> None:
        # Load cogs
        for cog in initial_cogs:
            self.logger.debug(f"Loading {cog}")
            await self.load_extension(cog)

        # Initialise persistent ClientSession
        self.session = aiohttp.ClientSession()
        self.logger.debug("Loading aiohttp session")

    async def on_ready(self) -> None:
        self.logger.info("\n\nBot successfully loaded\n")
        game = discord.Game("with your mom")
        await self.change_presence(status=discord.Status.idle, activity=game)
        return

    async def on_command_error(self, ctx: commands.Context, e: Exception) -> None:
        self.logger.error(e, exc_info=True)

        # If user made an error in their command
        if isinstance(e, UserError):
            await ctx.send(e.reason)
            return

        # If asyncio.TimeoutError is raised, ignore it
        elif isinstance(e, asyncio.TimeoutError):
            return

        if ctx.author.id == self.owner_id:
            await ctx.send(f"```{traceback.format_exc()}```")
            return

    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.logger.info(f"Bot joined guild {guild.name}")
        return

    async def on_guild_leave(self) -> None:
        return
