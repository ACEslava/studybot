import random
from typing import TYPE_CHECKING

import discord
import pint
from discord.ext import commands
from quantulum3 import parser

if TYPE_CHECKING:
    from studybot import StudyBot


class OnHandling(commands.Cog):
    def __init__(self, bot: "StudyBot"):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: "discord.Message"):
        if not message.author.bot:
            if message.content.lower() == "hello friends":
                await message.channel.send(f"Hello <@{message.author.id}> :D")
                self.bot.logger.info(f"Said hello to {message.author}")

            elif (
                any(
                    [
                        s in message.content.lower()
                        for s in ("intuit", "in2it", "intooit", "in tuit")
                    ]
                )
                and random.random() < 0.5
            ):
                if message.author.id == 459011326241669122 and random.random() < 0.4:
                    await message.channel.send("stop intuiting, hash")
                else:
                    await message.channel.send(
                        f"<@{message.author.id}> intuit deez nuts"
                    )

            elif any(
                [
                    s in message.content.lower()
                    for s in ("km", "mi", "ft", "cm", "in", "lb", "kg")
                ]
            ):
                try:
                    # Extract quantity from raw text
                    raw_quant = parser.parse(message.content.lower())

                    # Parse quantity into an object
                    parsed_quant: pint.Quantity = pint.UnitRegistry()(
                        raw_quant[0].surface
                    )

                    # Convert to imperial/metric equivalent
                    converted_quant = None
                    match parsed_quant.units:
                        case "kilometer":
                            converted_quant = parsed_quant.to("miles")
                        case "mile":
                            converted_quant = parsed_quant.to("kilometer")
                        case "foot":
                            converted_quant = parsed_quant.to("meter")
                        case "meter":
                            converted_quant = parsed_quant.to("foot")
                        case "inch":
                            converted_quant = parsed_quant.to("centimeter")
                        case "centimeter":
                            converted_quant = parsed_quant.to("inch")
                        case "pound":
                            converted_quant = parsed_quant.to("kilogram")
                        case "kilogram":
                            converted_quant = parsed_quant.to("pound")

                    # Send conversion to Discord
                    if isinstance(converted_quant, pint.Quantity):
                        u_before = format(parsed_quant, "~P")
                        u_after = format(round(converted_quant, 2), "~P")
                        embed = discord.Embed(
                            title="Unit Conversion",
                            description=f"{u_before} is {u_after}",
                        )
                        await message.channel.send(embed=embed)
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.logger.info(f"Bot joined guild {guild.name}")
        return

    @commands.Cog.listener()
    async def on_guild_leave(self) -> None:
        return

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=discord.Embed(
                description="Planned Service Disruption: Bot will be offline from "
                + "<t:1663398000:f> to <t:1663441200:f> due to infrastructure move"
            )
        )


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(OnHandling(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {OnHandling.__module__.__str__()}")
