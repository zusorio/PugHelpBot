import logging
import discord

from discord.ext import commands
from .helpers import Config, PingStatus
from .cogs.simple_ping import SimplePing
from .cogs.admin_tools import AdminTools
from .cogs.advanced_tools import AdvancedTools


def main():
    # Get discord logger
    log = logging.getLogger("discord")
    log.setLevel(logging.WARNING)
    handler = logging.StreamHandler()
    log.addHandler(handler)

    # Configure Logger
    # Configure logger
    log.setLevel(20)
    handler.setFormatter(logging.Formatter(
        "{asctime} [{levelname}] [{module}] {message}",
        style="{",
        datefmt="%H:%M:%S"
    ))

    # Create the config object and read config.json
    config = Config()

    # Create the PingStatus object
    ping_status = PingStatus()

    # Create bot object with prefix from config
    bot = commands.Bot(command_prefix=config.bot_prefix)
    bot.add_cog(SimplePing(bot, log, config, ping_status))
    bot.add_cog(AdminTools(bot, log, config))
    bot.add_cog(AdvancedTools(bot, log, config, ping_status))

    bot.run(config.token)

main()