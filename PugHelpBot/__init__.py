import logging
import discord

from .discord_handler import DiscordHandler
from discord.ext import commands
from .helpers import Config, PingStatus
from .cogs.simple_ping import SimplePing
from .cogs.admin_tools import AdminTools
from .cogs.advanced_tools import AdvancedTools
from .cogs.channel_clean import ChannelClean
from .cogs.initialize import Initialize


def main():
    # Create the config object and read config.json
    config = Config()

    # Configure logging format
    format = logging.Formatter(
        "{asctime} [{levelname}] [{module}] {message}",
        style="{",
        datefmt="%H:%M:%S"
    )

    # Get the discord logger
    log = logging.getLogger("discord")
    # Set logging level to debug for now
    log.setLevel(logging.INFO)

    # Create a handler that outputs INFO to stdout
    text_handler = logging.StreamHandler()
    text_handler.setLevel(logging.INFO)
    text_handler.setFormatter(format)
    log.addHandler(text_handler)

    # Create a handler that outputs WARNING to the discord webhook
    webhook_handler = DiscordHandler(config.log_webhook_token, config.log_name)
    webhook_handler.setLevel(logging.WARNING)
    webhook_handler.setFormatter(format)
    log.addHandler(webhook_handler)

    # Create the PingStatus object
    ping_status = PingStatus()

    # Create bot object with prefix from config
    bot = commands.Bot(command_prefix=config.bot_prefix)
    bot.add_cog(SimplePing(bot, log, config, ping_status))
    bot.add_cog(AdminTools(bot, log, config, ping_status))
    bot.add_cog(AdvancedTools(bot, log, config, ping_status))
    bot.add_cog(ChannelClean(bot, log, config, ping_status))
    bot.add_cog(Initialize(bot, log, config))
    log.warning("Starting Bot...")
    bot.run(config.token)


main()
