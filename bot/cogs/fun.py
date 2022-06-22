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
        return


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(Fun(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {Fun.__module__.__str__()}")
