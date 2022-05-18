import asyncio
import re
import time
from typing import TYPE_CHECKING

import aiohttp
import cchardet
import discord
from bs4 import BeautifulSoup, SoupStrainer
from cogs.search_engine_funcs.generic_search import Search
from discord.ext import commands
from functions.multi_page import PageTurnView

if TYPE_CHECKING:
    from bot.studybot import StudyBot


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
            ]
        )
        return

    async def __call__(self) -> None:
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

        def image_embed(image: BeautifulSoup) -> discord.Embed:
            """Generates Discord Embed from google result

            :param image: Raw HTML from BeautifulSoup
            :type image: BeautifulSoup
            :return: Discord embed of image
            :rtype: discord.Embed
            """
            try:
                # creates and formats the embed
                self.bot.logger.debug("Found image")
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
                    "Search results for:"
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

        def result_cleanup(soup: BeautifulSoup) -> set:
            """Filters HTML result for easier processing

            :param result: Raw HTML
            :type result: BeautifulSoup
            :return: Filtered HTML
            :rtype: set
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
            return {
                result
                for result in results
                if not any(
                    badResult in result.strings for badResult in wrong_first_results
                )
                or result.strings == ""
            }

        try:
            t0 = time.time()
            # gets the webscraped html of the google search
            session: aiohttp.ClientSession = self.bot.session
            async with session.get(
                self.url, headers={"User-Agent": "python-requests/2.25.1"}
            ) as data:
                html = await data.text()
                soup, index = (
                    BeautifulSoup(
                        html,
                        features="lxml",
                        parse_only=SoupStrainer("div", {"id": "main"}),
                    ),
                    3,
                )
            # remove cchardet import error
            _ = cchardet

            # Debug HTML output
            # with open('test.html', 'w', encoding='utf-8-sig') as file:
            #     file.write(soup.prettify())

            # if the search returns results
            if soup.find("div", {"id": "main"}) is not None:
                filtered_results = result_cleanup(soup)
                # checks if user searched specifically for images
                embeds = None

                # searches for the "images for" search result div
                for results in filtered_results:
                    if "Images" in results.strings:
                        images = results.findAll("img", recursive=True)

                        # checks if image wont embed properly
                        bad_urls = []

                        async def http_req(index, url):
                            try:
                                url = image_url_parser(url)
                            except Exception:
                                return

                            async with self.bot.session.get(
                                url, allow_redirects=False
                            ) as resp:
                                if resp.status == 301 or resp.status == 302:
                                    bad_urls.append(index)

                        try:
                            await asyncio.gather(
                                *[
                                    http_req(index, url)
                                    for index, url in enumerate(images)
                                ]
                            )
                        except aiohttp.InvalidURL:
                            break
                        if len(bad_urls) > 0:
                            images = [
                                img
                                for idx, img in enumerate(images)
                                if idx not in bad_urls
                            ]

                        # creates embed list
                        embeds = [
                            embed
                            for embed in list(map(image_embed, images))
                            if embed.description is not (None or "")
                        ]

                        if len(embeds) > 0:
                            del embeds[-1]
                        break

                if embeds is None or len(embeds) == 0:
                    embeds = [
                        embed
                        for embed in list(map(text_embed, filtered_results))
                        if embed.description is not (None or "")
                    ]

                    # Creates search groupings
                    new_embed_list = []
                    i = 0
                    combinedDesc = ""
                    for j in range(len(embeds)):
                        embed_desc = "\n".join(
                            list(filter(None, embeds[j].description.split("\n")))
                        )
                        if "image" in embeds[j].to_dict().keys():
                            combinedDesc = ""
                            new_embed_list.append([embeds[j]])
                            i = j
                            continue
                        else:
                            if len(combinedDesc + embed_desc) < 1048:
                                combinedDesc += "\n" + "\n" + embed_desc
                                continue

                            combinedDesc = ""
                            new_embed_list.append(embeds[i : j + 1])
                            i = j
                    new_embed_list.append(embeds[i : j + 1])

                    for idx, group in enumerate(new_embed_list):
                        if len(group) == 1:
                            continue
                        combinedDesc = ""
                        for embed in group:
                            combinedDesc += (
                                "\n"
                                + "\n"
                                + "\n".join(
                                    list(filter(None, embed.description.split("\n")))
                                )
                            )

                        new_embed_list[idx] = [
                            discord.Embed(
                                title=(
                                    "Search results for:"
                                    + f"{self.query[:233]}"
                                    + f"{'...' if len(self.query) > 233 else ''}"
                                ),
                                description=combinedDesc,
                                url=self.url,
                            )
                        ]

                    embeds = [i[0] for i in new_embed_list]

                # adds the page numbering footer to the embeds
                for index, item in enumerate(embeds):
                    item.set_footer(
                        text=(
                            "Page "
                            + f"{index+1}/{len(embeds)}"
                            + "\nRequested by: "
                            + f"{str(self.ctx.author)}"
                        )
                    )

                t1 = time.time()
                self.bot.logger.debug(
                    f"Search returned {len(embeds)} results in {round(t1-t0, 5)} sec"
                )
                current_page = 0
                await self.message.edit(
                    content="",
                    embed=embeds[current_page % len(embeds)],
                    view=PageTurnView(self.ctx, embeds, self.message, 60.0),
                )
                return

            else:
                self.bot.logger.debug("Search returned 0 results")
                embed = discord.Embed(
                    title=(
                        "Search results for: "
                        + f'{self.query[:233]}{"..." if len(self.query) > 233 else ""}'
                    ),
                    description="No results found. Maybe try another search term.",
                )

                embed.set_footer(text=f"Requested by {self.ctx.author}")

                await self.message.edit(
                    content="", embed=embed, view=PageTurnView(self.ctx, embeds)
                )

        except Exception as e:
            await self.message.delete()
            await self.bot.on_command_error(self.ctx, e)
