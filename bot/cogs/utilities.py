from discord.ext import commands
from studybot import StudyBot


class Utilities(commands.Cog):
    """Various miscellaneous utility commands"""

    def __init__(self, bot: StudyBot):
        self.bot = bot


async def setup(bot: StudyBot) -> None:
    await bot.add_cog(Utilities(bot))
