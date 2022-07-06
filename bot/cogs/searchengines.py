import asyncio
from typing import TYPE_CHECKING, List

from cogs.search_engine_funcs.generic_search import Search
from cogs.search_engine_funcs.google import GoogleSearch
from discord.ext import commands

if TYPE_CHECKING:
    import discord

    from studybot import StudyBot


class SearchEngines(commands.Cog):
    """Various Search Engine Commands"""

    def __init__(self, bot: "StudyBot"):
        self.bot = bot

    @commands.command(
        name="google",
        brief="Search through Google",
        usage="[query]",
        help=(
            "Google search. If a keyword is detected in [query],"
            + " a special function will activate"
        ),
        aliases=["g", "googel", "googlr", "googl", "gogle", "gogl", "foogle"],
    )
    @commands.cooldown(1, 3, commands.BucketType.default)
    async def google(self, ctx: commands.Context, *args):
        await self.__genericSearch(ctx, GoogleSearch, args)
        return

    async def __genericSearch(
        self, ctx: commands.Context, searchObject: Search, args: list
    ) -> None:
        """A generic search handler for bot search functions.

        Parameters
        ----------
        ctx : commands.context
            Discord Command Context
        searchObject : Search
            Search engine wrapper class
        args : list
            Raw arguments from Discord
        """

        # region args parsing
        if not args:  # checks if search is empty
            await ctx.send(
                "Enter search query or cancel"
            )  # if empty, asks user for search query
            try:
                usersearch: "discord.Message" = await self.bot.wait_for(
                    "message", check=lambda m: m.author == ctx.author, timeout=30
                )  # 30 seconds to reply
                if usersearch.content.lower() == "cancel":
                    raise self.bot.UserCancel

                search_args = usersearch.content.split("--")

            except asyncio.TimeoutError:
                await ctx.send(
                    f"{ctx.author.mention} Error: You took too long. Aborting"
                )  # aborts if timeout
            except Exception as e:
                raise e
        else:
            search_args = " ".join([query.strip() for query in list(args)]).split(
                "--"
            )  # turns multiword search into single string.

        userquery: str | None = search_args[0]
        # check if user actually searched something
        if userquery is None:
            return

        if len(search_args) > 1:
            search_args: List[str] = search_args[1:]
        else:
            search_args = None
        # endregion

        # allows users to edit their search query after results are returned
        continueLoop = True
        while continueLoop:
            try:
                self.bot.logger.info(
                    str(ctx.author) + " searched for: " + userquery[:233]
                )
                self.bot.logger.debug("Sending loading message")
                message = await ctx.send(self.bot.loading_message())

                await searchObject(
                    bot=self.bot,
                    ctx=ctx,
                    message=message,
                    args=search_args,
                    query=userquery,
                )()
                self.bot.logger.debug("Waiting for message edit")
                messageEdit = await self.bot.wait_for(
                    "message_edit",
                    check=lambda _, m: m.author == ctx.author and m == ctx.message,
                )
                self.bot.logger.debug("Message edit detected, looping search")
                await message.delete()

                userquery = messageEdit[1].content.replace(
                    f"&{ctx.invoked_with} ", ""
                )  # finds the new user query
                continue

            except TimeoutError:  # after a minute, everything cancels
                self.bot.logger.debug("Wait cancelled")
                await message.clear_reactions()
                continueLoop = False
                return

            except Exception as e:
                raise e
        return


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(SearchEngines(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {SearchEngines.__module__.__str__()}")
