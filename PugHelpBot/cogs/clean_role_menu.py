from ..helpers import send_ping, Config, get_unique_message_react_users, PingStatus
import logging
import discord
from discord.ext import commands


class CleanRoleMenu(commands.Cog):
    """Cog for cleaning role menus"""
    def __init__(self, bot: commands.Bot, log: logging.Logger, config: Config, ping_status: PingStatus):
        self.bot = bot
        self.log = log
        self.config = config
        self.ping_status = ping_status

        self.log.info("Loaded Cog CleanRoleMenu")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        user = self.bot.get_guild(payload.guild_id).get_member(payload.user_id)

        if payload.message_id in self.config.role_menus:
            role_menu_allowed_emoji = ["✅", "partblob"]
            if payload.emoji.name not in role_menu_allowed_emoji:
                reacted_message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await reacted_message.remove_reaction(payload.emoji, user)
                await user.send("Please don't add spam reactions to this message!")
