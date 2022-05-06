from discord.ext import commands
from searchio import SearchIO


class Utilities(commands.Cog):
    """Various miscellaneous utility commands"""

    def __init__(self, bot: SearchIO):
        self.bot = bot


async def setup(bot: SearchIO) -> None:
    await bot.add_cog(Utilities(bot))
