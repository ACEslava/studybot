import asyncio
import os
import time
import traceback
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

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

            elif any(
                [
                    s in message.content.lower()
                    for s in (
                        "intuit",
                        "in2it",
                        "intooit",
                    )
                ]
            ):
                await message.channel.send(f"<@{message.author.id}> intuit deez nuts")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        self.bot.logger.info(str(ctx.author) + " used " + ctx.command.name)

        # Log all command uses
        if os.getenv("DEBUG_MODE") != "true":
            embed = discord.Embed(
                title=ctx.command.name, description=ctx.message.content
            )
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            embed.set_footer(text=time.asctime())
            await self.bot.logging_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, e: Exception) -> None:
        # If user made an error in their command
        if isinstance(e, self.bot.UserError):
            await ctx.send(embed=discord.Embed(description=e.reason))
            return

        # If certain errors are raised, ignore it
        elif isinstance(
            e,
            (
                TimeoutError,
                asyncio.TimeoutError,
                commands.errors.CommandNotFound,
                commands.errors.CheckFailure,
            ),
        ):
            return

        # Cooldown
        elif isinstance(e, commands.errors.CommandOnCooldown):
            await ctx.send(
                embed=discord.Embed(
                    description="Command on cooldown. Wait "
                    + f"{round(e.retry_after, 2)} sec"
                )
            )
            self.bot.logger.info("Command ratelimited")
            return
        self.bot.logger.error(e, exc_info=True)

        if ctx.author.id == self.bot.owner_id:
            await ctx.send(f"```{e}{chr(10)}{traceback.format_exc()}```")
        else:
            err_embed = discord.Embed(
                title=":(",
                description=(
                    "An unknown error has occurred,"
                    + " please try a different command."
                ),
            )
            await ctx.send(embed=err_embed)
            return


async def setup(bot: "StudyBot") -> None:
    await bot.add_cog(OnHandling(bot))


async def teardown(bot: "StudyBot") -> None:
    bot.logger.debug(f"Unloading {OnHandling.__module__.__str__()}")
