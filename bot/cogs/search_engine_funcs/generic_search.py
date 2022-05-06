from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import discord
    from discord.ext import commands
    from studybot import StudyBot


class Search:
    def __init__(
        self,
        bot: "StudyBot",
        ctx: "commands.Context",
        message: "discord.Message",
        args: list,
        query: str,
    ):

        self.bot = bot
        self.ctx = ctx
        self.message = message
        self.args = args if args is not None else []
        self.query = query
