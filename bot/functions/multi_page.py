from typing import List

import discord
from discord.ext import commands

from studybot import StudyBot


class PageTurnView(discord.ui.View):
    """discord.ui.View subclass for page-turn functionality between embeds
    Parameters
    ----------
    bot : StudyBot
        Bot instance
    ctx : discord.ext.commands.Context
        Discord's command context
    embed_list: List[discord.Embed]
        List of embeds to page turn
    message: discord.Message
        The message containing the buttons.
    timeout: float
        (Optional) Float indicating seconds before timeout. (Default=60.0)

    Raises
    ----------
    TimeoutError: on timeout expiry
    """

    def __init__(
        self,
        bot: StudyBot,
        ctx: commands.Context,
        embed_list: List[discord.Embed],
        message: discord.Message,
        timeout=60.0,
    ):
        self.bot = bot
        self.ctx = ctx
        self.embed_list = embed_list
        self.current_page = 0
        self.message = message

        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Checks if user or bot dev interacted
        return any(
            (
                interaction.user.id == self.ctx.message.author.id,
                interaction.user.id == self.bot.owner_id,
            )
        )

    # Remove buttons on timeout
    async def on_timeout(self) -> None:
        super().clear_items()
        try:
            await self.message.edit(view=self)
        except Exception:
            pass
        super().stop()
        return

    # Delete result
    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.red)
    async def delete_callback(self, interaction: discord.Interaction, _):
        await interaction.message.delete()
        # Post delete cleanup
        self.bot.logger.debug("User deleted message")
        super().clear_items()
        super().stop()
        return

    # Prev page
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.gray)
    async def prev_callback(self, interaction: discord.Interaction, _):
        try:
            self.current_page -= 1
            await interaction.response.edit_message(
                content="",
                embed=self.embed_list[self.current_page % len(self.embed_list)],
            )
        except Exception:
            super().clear_items()
            await self.message.edit(view=super())
            super().stop()

    # Next page
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.gray)
    async def next_callback(self, interaction: discord.Interaction, _):
        try:
            self.current_page += 1
            await interaction.response.edit_message(
                content="",
                embed=self.embed_list[self.current_page % len(self.embed_list)],
            )
        except Exception:
            super().clear_items()
            await self.message.edit(view=super())
            super().stop()
