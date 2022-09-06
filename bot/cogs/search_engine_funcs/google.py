import asyncio
import re
import time
from typing import TYPE_CHECKING, List

import cchardet
import discord
import validators
from bs4 import BeautifulSoup, SoupStrainer
from cogs.search_engine_funcs.generic_search import Search
from discord.ext import commands
from functions.multi_page import PageTurnView

if TYPE_CHECKING:
    from studybot import StudyBot


class GoogleSearch(Search):
    def __init__(
        self,
        bot: "StudyBot",
        ctx: commands.Context,
        message: discord.Message,
        args: list,
        query: str,
    ):
        super().__init__(bot, ctx, message, args, query)

        # creates google search url
        # https://google.com/search?
        #   q=[query]
        #   &num=[number of results]
        #   &safe=[safesearch status]
        #   &pws=0

        rm_img = "+-stock+-pinterest" if bool(re.search("image", query.lower())) else ""
        self.url = "".join(
            [
                "https://google.com/search?pws=0&q=",
                self.query.replace(" ", "+"),
                f"{rm_img}",
                "&safe=active",
                "&uule=w+CAIQICI5TW91bnRhaW4gVmlldyxTYW50YS",
                "BDbGFyYSBDb3VudHksQ2FsaWZvcm5pYSxVbml0ZWQgU3RhdGVz",
                "&num=10",
            ]
        )
        return

    async def __call__(self) -> None:
        """Performs Google search

        Raises
        ----------
        Search.NoResults : when no results are found
        asyncio.TimeoutError : when any interaction expires
        """

        def link_unicode_parse(link: str) -> str:
            """Parses unicode codes into characters

            :param link: url to parse
            :type link: str
            :return: parsed url
            :rtype: str
            """
            return re.sub(r"%(.{2})", lambda m: chr(int(m.group(1), 16)), link)

        def image_url_parser(image: str) -> str:
            """Extracts image URL from google url string

            :param image: URL to parse
            :type image: str
            :return: Parsed URL
            :rtype: str
            """
            try:
                # searches html for image urls
                imgurl = link_unicode_parse(
                    re.findall(
                        "(?<=imgurl=).*(?=&imgrefurl)", image.parent.parent["href"]
                    )[0]
                )
                if "encrypted" in imgurl:
                    imgurl = re.findall(
                        "(?<=imgurl=).*(?=&imgrefurl)",
                        image.findAll("img")[1].parent.parent["href"],
                    )[0]

                return imgurl
            except Exception:
                return ""

        def text_embed(result: BeautifulSoup) -> discord.Embed:
            """Generates Discord Embed for Google result

            :param result: Raw HTML from BeautifulSoup
            :type result: BeautifulSoup
            :return: Discord Embed
            :rtype: discord.Embed
            """
            # creates and formats the embed

            result_embed = discord.Embed(
                title=(
                    "Search results for: "
                    + f'{self.query[:233]}{"..." if len(self.query) > 233 else ""}'
                )
            )

            # google results are separated by divs
            # searches for link in div
            find_link = result.find_all("a", href_="")
            link_list = tuple(a for a in find_link if not a.find("img"))
            link = None
            if len(link_list) != 0:
                try:
                    # parses link from html
                    link = link_unicode_parse(
                        re.findall(r"(?<=url\?q=).*(?=&sa)", link_list[0]["href"])[0]
                    )
                except Exception:
                    pass

            # extracts all meaningful text in the search result by div
            result_find = result.findAll("div")
            divs = tuple(d for d in result_find if not d.find("div"))
            titleinfo = [
                " ".join(
                    [
                        string if string != "View all" else ""
                        for string in div.stripped_strings
                    ]
                )
                for div in divs[:2]
            ]
            titleinfo = [f"**{ti}**" for ti in titleinfo if ti != ""]
            if link is not None:
                titleinfo[-1] = link

            lines = [
                " ".join(
                    [
                        string if string != "View all" else ""
                        for string in div.stripped_strings
                    ]
                )
                for div in divs[2:]
            ]

            printstring = "\n".join(titleinfo + lines)

            # discord prevents embeds longer than 2048 chars
            # truncates adds ellipses to strings longer than 2048 chars
            if len(printstring) > 1024:
                printstring = printstring[:1020] + "..."

            # sets embed description to string
            result_embed.description = re.sub("\n\n+", "\n\n", printstring)

            # tries to add an image to the embed
            image = result.find("img")
            try:
                result_embed.set_image(url=image_url_parser(image))
            except Exception:
                pass
            result_embed.url = self.url
            return result_embed

        def featured_snippet_embed(result: BeautifulSoup) -> discord.Embed:
            """Generates Discord Embed for Google Featured Snippet

            :param result: Raw HTML from BeautifulSoup
            :type result: BeautifulSoup
            :return: Discord Embed
            :rtype: discord.Embed
            """
            # creates and formats the embed

            result_embed = discord.Embed(
                title=(
                    "[BETA] Featured Snippet: "
                    + f'{self.query[:220]}{"..." if len(self.query) > 220 else ""}'
                )
            )

            # extracts all meaningful text in the search result by div
            printstring = "\n".join(
                [
                    "\n".join(
                        [
                            string if string != "View all" else ""
                            for string in tuple(div.stripped_strings)[:2]
                        ]
                    )
                    for div in result
                ]
            )

            # discord prevents embeds longer than 2048 chars
            # truncates adds ellipses to strings longer than 2048 chars
            if len(printstring) > 1024:
                printstring = printstring[:1020] + "..."

            # sets embed description to string
            result_embed.description = re.sub("\n\n+", "\n\n", printstring)
            result_embed.url = self.url
            return result_embed

        def result_cleanup(soup: BeautifulSoup) -> List[BeautifulSoup]:
            """Filters HTML result for easier processing

            :param result: Raw HTML
            :type result: BeautifulSoup
            :return: Filtered HTML
            :rtype: list
            """
            # html div cleanup
            results = soup.find("div", {"id": "main"}).contents
            results = [
                results[resultNumber] for resultNumber in range(3, len(results) - 2)
            ]

            # bad divs to discard
            wrong_first_results = {
                "Did you mean: ",
                "Showing results for ",
                "Tip: ",
                "See results about",
                "Related searches",
                "Including results for ",
                "Top stories",
                "People also ask",
                "Next >",
            }
            # bad div filtering
            return [
                result
                for result in results
                if not any(
                    badResult in result.strings for badResult in wrong_first_results
                )
                or result.strings == ""
            ]

        async def image_results(results: set) -> List[discord.Embed]:
            """Finds images from results

            Parameters
            ----------
            results : set
                set of BeautifulSoup parsed HTML results

            Returns
            -------
            List[discord.Embed]
                List of image embeds
            """

            def image_embed(image: BeautifulSoup) -> discord.Embed:
                """Generates Discord Embed from google result

                :param image: Raw HTML from BeautifulSoup
                :type image: BeautifulSoup
                :return: Discord embed of image
                :rtype: discord.Embed
                """
                try:
                    # creates and formats the embed
                    result_embed = discord.Embed(
                        title=f"Search results for: {self.query[:233]}"
                        f'{"..." if len(self.query) > 233 else ""}'
                    )

                    # sets the discord embed to the image
                    result_embed.set_image(url=image_url_parser(image))
                    result_embed.url = self.url
                except Exception:
                    result_embed.set_image(
                        url=(
                            "https://external-preview.redd.it/"
                            + "9HZBYcvaOEnh4tOp5EqgcCr_vKH7cjFJwkvw-45Dfjs.png?"
                            + "auto=webp&s=ade9b43592942905a45d04dbc5065badb5aa3483"
                        )
                    )
                finally:
                    return result_embed

            async def url_validation(url: str) -> bool:
                """Validates if provided URL links to an image

                Parameters
                ----------
                url : str
                    Unparsed URL of image

                Returns
                -------
                bool
                    True if valid URL
                """
                try:
                    url = image_url_parser(url)
                    async with self.bot.session.head(
                        url, allow_redirects=False
                    ) as resp:
                        return resp.status < 300 and validators.url(url)
                except Exception:
                    return False

            # searches for the "images for" search result div
            for result in results:
                if "Images" in result.strings:
                    images = result.findAll("img", recursive=True)
                    tasks = [asyncio.create_task(url_validation(url)) for url in images]
                    # checks if image wont embed properly
                    good_url_mask = await asyncio.gather(*tasks)
                    images = [
                        i for (i, v) in zip([url for url in images], good_url_mask) if v
                    ]

                    # creates embed list
                    embeds = [
                        embed
                        for embed in list(map(image_embed, images))
                        if embed.description is not (None or "")
                    ]

                    return embeds

        try:
            t0 = time.time()

            # checks if image is in search query
            self.bot.logger.debug("Checking if user searched for image")
            if bool(re.search("image", self.query.lower())):
                has_found_image = True
            else:
                has_found_image = False

            # gets the webscraped html of the google search
            self.bot.logger.debug("Retrieving google html")
            async with self.bot.session.get(
                self.url, headers={"User-Agent": "python-requests/2.25.1"}
            ) as data:
                html = await data.text()
                soup = BeautifulSoup(
                    html,
                    features="lxml",
                    parse_only=SoupStrainer("div", {"id": "main"}),
                )

            # remove cchardet import error
            _ = cchardet

            # Debug HTML output
            # with open("test.html", "w", encoding="utf-8-sig") as file:
            #     file.write(soup.prettify())

            # if the search returns results
            if soup.find("div", {"id": "main"}) is None:
                self.bot.logger.debug("Search returned 0 results")
                raise Search.NoResults
            embeds = []
            self.bot.logger.debug("Cleaning results")
            filtered_results = result_cleanup(soup)

            # checks if user searched specifically for images, else use text embed
            if has_found_image:
                self.bot.logger.debug("User searched for images, parsing image results")
                embeds = await image_results(filtered_results)
            else:
                self.bot.logger.debug("Parsing text results")

                # Remove featured snippet from result
                for idx, val in enumerate(filtered_results):
                    if "Featured Snippets" in val.text:
                        filtered_results.pop(idx)
                        break

                # Creates embed list
                embeds = [
                    embed
                    for embed in map(text_embed, filtered_results)
                    if embed.description is not (None or "")
                ]

                # Add featured snippet to beginning
                # Gx5Zad xpd EtOod pkphOe is Google obsfucation
                featured_snippet = soup.find(
                    "div", {"class": "Gx5Zad xpd EtOod pkphOe"}
                )
                if featured_snippet is not None:
                    embeds.insert(0, featured_snippet_embed(featured_snippet))

            if embeds is None or len(embeds) == 0:
                raise Search.NoResults

            # adds the page numbering footer to the embeds
            embeds = [
                e.set_footer(
                    text=(
                        "Page "
                        + f"{i+1}/{len(embeds)}"
                        + "\nRequested by: "
                        + f"{str(self.ctx.author)}"
                    )
                )
                for i, e in enumerate(embeds)
            ]

            self.bot.logger.debug(
                f"Search returned {len(embeds)} "
                + f"results in {round(time.time()-t0, 5)} sec"
            )

            view = PageTurnView(self.bot, self.ctx, embeds, self.message, 60)
            await self.message.edit(
                content="",
                embed=embeds[0],
                view=view,
            )

            await view.wait()
            raise asyncio.TimeoutError

        except (asyncio.TimeoutError, Search.NoResults):
            raise

        except Exception as e:
            await self.message.delete()
            await self.bot.on_command_error(self.ctx, e)
