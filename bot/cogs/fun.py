import random
from typing import TYPE_CHECKING

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
        session: aiohttp.ClientSession = self.bot.session
        async with session.get("https://api.thecatapi.com/v1/images/search") as data:
            json = await data.json()

        embed = discord.Embed()
        embed.set_image(url=json[0]["url"])
        embed.set_footer(text=f"Requested by {ctx.author}")
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
        session: aiohttp.ClientSession = self.bot.session
        async with session.get("https://dog.ceo/api/breeds/image/random") as data:
            json = await data.json()

        embed = discord.Embed()
        embed.set_image(url=json["message"])
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)
        self.bot.logger.info(f"Sent image: {json['message']}")
        return

    @commands.command(
        name="8ball",
        description="Answers your deepest yes/no questions",
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
        embed = discord.Embed(title="8ball", description=random.choice(responses))
        embed.set_footer(f"Requested by {ctx.author}")
        ctx.send(embed=embed)
        return

    @commands.command(
        name="boobs",
        description="Sends a random picture of boobs (NSFW channels only)",
    )
    @commands.is_nsfw()
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def boobs(self, ctx: commands.Context):
        # Queries reddit API
        session: aiohttp.ClientSession = self.bot.session
        async with session.get(
            "https://www.reddit.com/r/boobs.json?sort=new&limit=100"
        ) as data:
            json = await data.json()

        # Finds random image post
        while 1:
            img_data: dict = random.choice(json["data"]["children"])
            if "url_overridden_by_dest" in img_data["data"].keys():
                if any(
                    url in img_data["data"]["url_overridden_by_dest"]
                    for url in ("i.imgur", "i.redd.it")
                ):
                    img: str = img_data["data"]["url_overridden_by_dest"]
                    break

        embed = discord.Embed()
        embed.set_image(url=img)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)
        self.bot.logger.info(f"Sent image: {img}")
        return


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(Fun(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {Fun.__module__.__str__()}")
