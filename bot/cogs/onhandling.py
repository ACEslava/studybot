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
        if (
            message.author.id == 399913903464644610
            and message.content.lower() == "hello friends"
        ):
            await message.channel.send("Hello <@399913903464644610>")
            self.bot.logger.info("Said hello to Ricky")

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        self.bot.logger.info(str(ctx.author) + "used" + ctx.command.name)


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(OnHandling(bot))
