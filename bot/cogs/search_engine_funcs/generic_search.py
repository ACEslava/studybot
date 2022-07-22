from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import discord
    from discord.ext import commands

    from studybot import StudyBot


class Search:
    """Internal base class for all search functions

    When called, execute search function

    return None

    raise Search.NoResults if no results are found

    raise asyncio.Timeout when any user-facing timeout expires
    """

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

    class NoResults(Exception):
        pass
