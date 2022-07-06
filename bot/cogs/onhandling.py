import os
import time
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from studybot import StudyBot


class OnHandling(commands.Cog):
    def __init__(self, bot: "StudyBot"):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: "discord.Message"):
        if message.content.lower() == "hello friends":
            await message.channel.send(f"Hello <@{message.author.id}> :D")
            self.bot.logger.info(f"Said hello to {message.author}")

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        self.bot.logger.info(str(ctx.author) + " used " + ctx.command.name)

        # Log all command uses
        if os.getenv("DEBUG_MODE") != "true":
            embed = discord.Embed(
                title=ctx.command.name, description=ctx.message.content
            )
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            embed.set_footer(text=time.asctime())
            await self.bot.logging_channel.send(embed=embed)


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(OnHandling(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {OnHandling.__module__.__str__()}")
