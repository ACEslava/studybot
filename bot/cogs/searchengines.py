import asyncio
from typing import TYPE_CHECKING

from cogs.search_engine_funcs.generic_search import Search
from cogs.search_engine_funcs.google import GoogleSearch
from discord.ext import commands

if TYPE_CHECKING:
    from bot.studybot import StudyBot


class SearchEngines(commands.Cog):
    """Various Search Engine Commands"""

    def __init__(self, bot: "StudyBot"):
        self.bot = bot

    @commands.command(
        name="google",
        brief="Search through Google",
        usage="google [query]",
        help=(
            "Google search. If a keyword is detected in [query],"
            + " a special function will activate"
        ),
        description="\n".join(
            [
                "translate: Uses Google Translate API to translate languages.",
                (
                    "\n     Input auto detects language unless "
                    + "specified with 'from [language]'"
                ),
                (
                    "\n     Defaults to output English OR user locale if set,"
                    + " unless explicitly specified with 'to [language]'"
                ),
                "\n     Example Query: translate مرحبا from arabic to spanish",
                "\n\nimage: Searches only for image results.",
                (
                    "\n\ndefine: Queries dictionaryapi.dev for"
                    + " an English definition of the word"
                ),
                (
                    "\n\nweather: Queries openweathermap for "
                    + "weather information at the specified location"
                ),
            ]
        ),
        aliases=["g", "googel", "googlr", "googl", "gogle", "gogl", "foogle"],
    )
    @commands.cooldown(1, 3, commands.BucketType.default)
    async def google(self, ctx: commands.Context, *args):
        await self.genericSearch(ctx, GoogleSearch, args)
        return

    async def genericSearch(
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
                userquery = await self.bot.wait_for(
                    "message", check=lambda m: m.author == ctx.author, timeout=30
                )  # 30 seconds to reply
                if userquery.content.lower() == "cancel":
                    raise self.bot.UserCancel
                else:
                    userquery = userquery.content.split("--")

            except asyncio.TimeoutError:
                await ctx.send(
                    f"{ctx.author.mention} Error: You took too long. Aborting"
                )  # aborts if timeout
            except Exception as e:
                raise e
        else:
            userquery = " ".join([query.strip() for query in list(args)]).split(
                "--"
            )  # turns multiword search into single string.

        if len(userquery) > 1:
            args = userquery[1:]
        else:
            args = None

        userquery = userquery[0]
        # check if user actually searched something
        if userquery is None:
            return
        # endregion

        # allows users to edit their search query after results are returned
        continueLoop = True
        while continueLoop:
            try:
                self.bot.logger.info(
                    str(ctx.author) + " searched for: " + userquery[:233]
                )
                message = await ctx.send(self.bot.loading_message())
                messageEdit = asyncio.create_task(
                    self.bot.wait_for(
                        "message_edit",
                        check=lambda _, m: m.author == ctx.author and m == ctx.message,
                    )
                )

                search = asyncio.create_task(
                    searchObject(
                        bot=self.bot,
                        ctx=ctx,
                        message=message,
                        args=args,
                        query=userquery,
                    )()
                )

                # checks for message edit
                waiting = [messageEdit, search]
                done, waiting = await asyncio.wait(
                    waiting, return_when=asyncio.FIRST_COMPLETED
                )

                # Task error handling
                for t in done:
                    if isinstance(t.exception(), Exception):
                        raise t.exception()

                if messageEdit in done:
                    if type(messageEdit.exception()) == TimeoutError:
                        raise TimeoutError
                    await message.delete()
                    messageEdit.cancel()
                    search.cancel()

                    messageEdit = messageEdit.result()
                    userquery = messageEdit[1].content.replace(
                        f"&{ctx.invoked_with} ", ""
                    )  # finds the new user query
                    continue
                else:
                    raise TimeoutError

            except TimeoutError:  # after a minute, everything cancels
                await message.clear_reactions()
                messageEdit.cancel()
                search.cancel()
                continueLoop = False
                return

            except Exception as e:
                raise e
        return


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(SearchEngines(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {SearchEngines.__module__.__str__()}")
