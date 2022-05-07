from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    import discord

    from studybot import StudyBot


class OnHandling(commands.Cog):
    def __init__(self, bot: StudyBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(message: discord.Message):
        if (
            message.author.id == 399913903464644610
            and message.content.lower() == "hello friends"
        ):
            await message.channel.send("Hello <@399913903464644610>")


async def setup(bot: StudyBot) -> None:
    await bot.add_cog(OnHandling(bot))
