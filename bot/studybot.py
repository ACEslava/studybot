import logging
import os
import traceback

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
            level=(
                logging.DEBUG if os.getenv("DEBUG_MODE") == "true" else logging.INFO
            ),
        )
        self.logger = logging.getLogger(__name__)

    async def setup_hook(self) -> None:
        # Load cogs
        for cog in initial_cogs:
            self.logger.info(f"Loading {cog}")
            await self.load_extension(cog)

        # Initialise persistent ClientSession
        self.session = aiohttp.ClientSession()
        self.logger.info("Loading aiohttp session")

    async def on_ready(self) -> None:
        self.logger.info("Bot successfully loaded")
        game = discord.Game("with your mom")
        await self.change_presence(status=discord.Status.idle, activity=game)
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
