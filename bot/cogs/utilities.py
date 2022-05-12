from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from studybot import StudyBot


class Utilities(commands.Cog):
    """Various miscellaneous utility commands"""

    def __init__(self, bot: "StudyBot"):
        self.bot = bot

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, *args):
        extensions = tuple(self.bot.extensions.keys())
        success_cog: str = ""
        try:
            for ext in extensions:
                await self.bot.reload_extension(ext)
                self.bot.logger.info(f"Reloaded {ext}")
                success_cog += "\n" + f" {ext}"
        except Exception:
            pass
        await ctx.send(f"Reloaded ```{success_cog}```")


async def setup(bot: "StudyBot") -> None:
    bot.logger.debug(f"Loading {Utilities.__module__.__str__()}")
    await bot.add_cog(Utilities(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {Utilities.__module__.__str__()}")
