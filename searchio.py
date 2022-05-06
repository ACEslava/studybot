import logging
import os
import traceback

import aiohttp
import discord
from discord.ext import commands

from functions.loading_message import get_loading_message

initial_cogs = ("cogs.utilities", "cogs.searchengines")
default_command_prefix = "&"
bot_owner = int(os.environ["OWNER_ID"])
application_id = os.environ["APPLICATION_ID"]


class SearchIO(commands.Bot):
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
    """

    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=default_command_prefix,
            intents=intents,
            owner_id=bot_owner,
            application_id=application_id,
        )

        # Initialise loading message function
        self.loading_message = get_loading_message

        # Set up logging
        logging.basicConfig(
            format="%(asctime)s %(name)s [%(levelname)s]: %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger(__name__)

    async def setup_hook(self) -> None:
        # Load cogs
        for cog in initial_cogs:
            self.logger.debug(f"Loading {cog}")
            await self.load_extension(cog)

        # Initialise persistent ClientSession
        self.session = aiohttp.ClientSession()
        self.logger.debug("Loading aiohttp session")

    async def on_ready(self) -> None:
        self.logger.info("Bot successfully loaded")
        return

    async def on_command_error(self, ctx: commands.Context, e: Exception) -> None:
        self.logger.critical(e, exc_info=True)
        if ctx.author.id == self.owner_id:
            await ctx.send(f"```{traceback.format_exc()}```")
        return

    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.logger.info(f"Bot joined guild {guild.name}")
        return

    async def on_guild_leave(self) -> None:
        return
