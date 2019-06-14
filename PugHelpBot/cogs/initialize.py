from ..helpers import Config
import logging
import discord
from discord.ext import commands


class Initialize(commands.Cog):
    """Cog for doing init stuff like setting rich presence"""

    def __init__(self, bot: commands.Bot, log: logging.Logger, config: Config):
        self.bot = bot
        self.log = log
        self.config = config

        self.log.info("Loaded Cog Initialize")

    @commands.Cog.listener()
    async def on_ready(self):
        # Set rich presence and inform us once the bot is ready
        await self.bot.change_presence(status=discord.Status.online,
                                       activity=discord.Game(f"PUGS (Prefix {self.config.bot_prefix})"))
        self.log.warning(f"\nCurrent config:\nPrefix: {self.config.bot_prefix}\nRequired reacts: {self.config.min_reacts}\nTime until cleanup {self.config.delete_after_hours} hours\nAvoid delete reacts: {self.config.min_reacts - self.config.avoid_delete_react_threshold}")
        self.log.warning("Bot is ready, set rich presence")
