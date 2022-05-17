from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    import discord

    from studybot import StudyBot


class OnHandling(commands.Cog):
    def __init__(self, bot: "StudyBot"):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: "discord.Message"):
        if message.content.lower() == "hello friends":
            await message.channel.send(f"Hello <@{message.author.id}>")
            self.bot.logger.info(f"Said hello to {message.author}")

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        self.bot.logger.info(str(ctx.author) + " used " + ctx.command.name)


async def setup(bot: "StudyBot") -> None:
    bot.logger.debug(f"Loading {OnHandling.__module__.__str__()}")
    await bot.add_cog(OnHandling(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {OnHandling.__module__.__str__()}")
