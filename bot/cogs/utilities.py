import time
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

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
        await ctx.reply(f"Reloaded ```{success_cog}```")

    @commands.hybrid_command(
        name="ping", with_app_command=True, description="Checks API response time"
    )
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def ping(self, ctx: commands.Context):
        t0 = time.time()
        if ctx.interaction is None:
            msg = await ctx.reply("Testing")
            t1 = time.time()

            await msg.edit(
                content=None,
                embed=discord.Embed(
                    title="Ping",
                    description=f"Reply in {round((t1-t0)*1000, 2)} ms"
                    + "\n"
                    + f"API Latency: {round(self.bot.latency*1000, 2)} ms",
                ),
            )
        else:
            await ctx.interaction.response.send_message(
                content="Testing", ephemeral=True
            )
            t1 = time.time()

            await ctx.interaction.edit_original_message(
                content=None,
                embed=discord.Embed(
                    title="Ping",
                    description=f"Reply in {round((t1-t0)*1000, 2)} ms"
                    + "\n"
                    + f"API Latency: {round(self.bot.latency*1000, 2)} ms",
                ),
            )


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(Utilities(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {Utilities.__module__.__str__()}")
