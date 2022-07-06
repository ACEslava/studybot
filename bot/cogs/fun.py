import random
import time
from typing import TYPE_CHECKING, Tuple

import aiohttp
import discord
from discord.ext import commands

if TYPE_CHECKING:
    from studybot import StudyBot


class Fun(commands.Cog):
    """Various miscellaneous fun commands"""

    def __init__(self, bot: "StudyBot"):
        self.bot = bot

    @commands.command(
        name="cat",
        description="Sends a random photo of a cat, what more can you ask for",
    )
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def cat(self, ctx: commands.Context):
        # gets the webscraped html of the google search
        self.bot.logger.debug("Sending API request")
        t0 = time.time()
        session: aiohttp.ClientSession = self.bot.session
        async with session.get("https://api.thecatapi.com/v1/images/search") as data:
            json = await data.json()
        self.bot.logger.debug(f"API Response in {round(time.time()-t0, 5)} sec")

        self.bot.logger.debug("Creating Embed")
        embed = discord.Embed()
        embed.set_image(url=json[0]["url"])
        embed.set_footer(text=f"Requested by {ctx.author}")

        self.bot.logger.debug("Sending Embed")
        await ctx.send(embed=embed)
        self.bot.logger.info(f"Sent image: {json[0]['url']}")
        return

    @commands.command(
        name="dog",
        description="Sends a random photo of a dog, what more can you ask for",
    )
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def dog(self, ctx: commands.Context):
        # gets the webscraped html of the google search
        t0 = time.time()
        self.bot.logger.debug("Sending API request")
        session: aiohttp.ClientSession = self.bot.session
        async with session.get("https://dog.ceo/api/breeds/image/random") as data:
            json = await data.json()
        self.bot.logger.debug(f"API Response in {round(time.time()-t0, 5)} sec")

        self.bot.logger.debug("Creating Embed")
        embed = discord.Embed()
        embed.set_image(url=json["message"])
        embed.set_footer(text=f"Requested by {ctx.author}")

        self.bot.logger.debug("Sending Embed")
        await ctx.send(embed=embed)
        self.bot.logger.info(f"Sent image: {json['message']}")
        return

    @commands.command(
        name="8ball",
        description="Answers your deepest yes/no questions",
        aliases=["eightball"],
    )
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def eightball(self, ctx: commands.Context):
        responses = (
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        )
        embed = discord.Embed(
            title="8ball", description=responses[random.randint(0, 19)]
        )
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)
        return

    @commands.command(
        name="boobs",
        description="Sends a random picture of boobs (NSFW channels only)",
        help="Sourced from r/boobs, boobies, bustypetite, tittydrop",
        aliases=["boob", "boobies"],
    )
    @commands.is_nsfw()
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def boobs(self, ctx: commands.Context):
        # adds repeat checker if doesn't exist
        try:
            getattr(self.bot, "boobs_sentPosts")
            self.bot.boobs_sentPosts = {
                k: v
                for k, v in self.bot.boobs_sentPosts.items()
                if time.time() - v < 86400
            }

        except AttributeError:
            self.bot.boobs_sentPosts = {}

        urls = (
            "boobs",
            "boobies",
            "bustypetite",
            "tittydrop",
        )
        post_id = await self.__random_reddit_post(urls, ctx)
        self.bot.boobs_sentPosts[post_id] = time.time()
        return

    async def __random_reddit_post(
        self, subreddit: Tuple[str], ctx: commands.Context
    ) -> str:
        """_summary_

        Parameters
        ----------
        subreddit : Tuple[str]
            Tuple of subreddits (no r/)
        ctx : commands.Context
            Command context

        Returns
        -------
        id : str
            Reddit post id
        """
        # Queries reddit API
        img = ""
        self.bot.logger.debug("Sending API request")

        while img == "":
            t0 = time.time()
            url = (
                "https://www.reddit.com/r/"
                + subreddit[random.randint(0, len(subreddit) - 1)]
                + ".json?sort=new&limit=100"
            )
            session: aiohttp.ClientSession = self.bot.session
            async with session.get(url) as data:
                posts = (await data.json())["data"]["children"]
            self.bot.logger.debug(f"API Response in {round(time.time()-t0, 5)} sec")

            # Finds random image post, limited to 10 retries
            self.bot.logger.debug("Getting random post from response")
            for _ in range(10):
                img_data: dict = posts[random.randint(0, len(posts) - 1)]["data"]
                if "url_overridden_by_dest" in img_data.keys():
                    if (
                        any(  # permitted domains
                            url in img_data["url"] for url in ("i.imgur", "i.redd.it")
                        )
                        # prev. sent posts
                        and img_data["id"] not in self.bot.boobs_sentPosts.keys()
                    ):
                        img = img_data["url"]
                        break

        # Does not embed gif for compatibility
        if ".gifv" in img:
            await ctx.send(
                content="https://www.reddit.com/r/"
                + f"{img_data['subreddit']}/comments/{img_data['id']}"
                + "\n"
                + img
            )
        else:
            self.bot.logger.debug("Creating Embed")
            embed = discord.Embed(
                title=img_data["title"],
                url="https://www.reddit.com/r/"
                + f"{img_data['subreddit']}/comments/{img_data['id']}",
            )

            embed.set_image(url=img)
            embed.set_footer(text=f"Requested by {ctx.author}")
            self.bot.logger.debug("Sending Embed")
            await ctx.send(embed=embed)
        self.bot.logger.info(f"Sent image: {img}")
        return img_data["id"]


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(Fun(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {Fun.__module__.__str__()}")
