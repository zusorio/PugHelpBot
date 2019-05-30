from ..helpers import Config, PingStatus, is_advanced, send_ping, get_unique_message_react_users
import logging
import discord
from discord.ext import commands


class AdvancedTools(commands.Cog):
    """Cog for doing advanced commands like mod_ping"""

    def __init__(self, bot: commands.Bot, log: logging.Logger, config: Config, ping_status: PingStatus):
        self.bot = bot
        self.log = log
        self.config = config
        self.ping_status = ping_status

        self.log.info("Loaded Cog AdvancedTools")

    @commands.command()
    @commands.check(is_advanced)
    async def mod_ping(self, ctx: discord.ext.commands.context.Context, message: discord.Message):
        # Bypasses all checks and just pings for any message. Just give it any message ID
        users_to_mention = await get_unique_message_react_users(message)
        await send_ping(message, users_to_mention)
        # Tell the user that everything is done.
        await ctx.author.send(
            "I mentioned all the people who reacted to your post in that channel. Make sure to put a message "
            "there telling them which lobby to join!")
        # Add the message to the already_pinged and already_notified list
        # Note: this does not prevent repeat staff pings
        self.ping_status.add_already_notified(message.id)
        self.ping_status.add_already_pinged(message.id)

    @mod_ping.error
    async def change_min_reacts_error(self, ctx: discord.ext.commands.context.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send("Sorry, something went wrong... You don't have permission to do that!")
        else:
            await ctx.author.send(error)
            self.log.info(error)
