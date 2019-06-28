from ..helpers import send_ping, Config, get_unique_message_react_users, PingStatus
import logging
import discord
from discord.ext import commands


class SimplePing(commands.Cog):
    """Cog for doing the regular ping reminders and checked pings"""
    def __init__(self, bot: commands.Bot, log: logging.Logger, config: Config, ping_status: PingStatus):
        self.bot = bot
        self.log = log
        self.config = config
        self.ping_status = ping_status

        self.log.info("Loaded Cog SimplePing")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, _):
        # If the reaction is on a message in the specified channels and wasn't pinged and notified for
        if reaction.message.channel.name in self.config.allowed_channels:
            if reaction.message.id not in self.ping_status.get_already_notified_simple():
                if reaction.message.id not in self.ping_status.get_already_pinged_simple():
                    # Get all unique users that reacted
                    unique_reacts = await get_unique_message_react_users(reaction.message)
                    # If there are the minimum of required reacts
                    if len(unique_reacts) >= self.config.min_reacts:
                        # Send the user instructions on how to mention all of the reactants
                        # The command the user is told to use is (prefix)ping MESSAGE_ID_OF_ORIGINAL_POST
                        await reaction.message.author.send(
                            f"Your LFP Post reached the minimum of {self.config.min_reacts} reacts!\n"
                            f"Reply with `{self.config.bot_prefix}ping {reaction.message.id}` "
                            f"__**in this DM**__  to ping the people that want to join!")
                        # Mark the message to not notify the user again
                        self.ping_status.add_already_notified(reaction.message.id)

    @commands.command()
    async def ping(self, ctx: discord.ext.commands.context.Context, message: discord.Message):
        """
        Ping the reactants to the message ID. Has checks for channel+min reacts
        :param ctx: Discord context
        :param message: The message ID of the message to ping for. The user get's this sent in the command they are told to use.
        :return: Nothing
        """

        # Make sure that the message is in a correct channel and that we haven't pinged for it yet
        if message.channel.name in self.config.allowed_channels and message.id not in self.ping_status.get_already_pinged_simple():
            # Get all the users we need the mention for that message
            users_to_mention = await get_unique_message_react_users(message)
            # Make sure there are actually enough users for a ping
            if len(users_to_mention) >= self.config.min_reacts:
                await send_ping(message, users_to_mention)
                # Add the message to the already_pinged list so that the user doesn't ping for the same message twice
                self.ping_status.add_already_pinged(message.id)
                # Tell the user that everything is done.
                await ctx.author.send(
                    "I mentioned all the people who reacted to your post in that channel. Make sure to put a message "
                    "there telling them which lobby to join!")
            else:
                # Warn the user that there are not enough reactions.
                await ctx.author.send(
                    "The message doesn't have enough reacts yet! Don't try and write commands manually. I'll tell you "
                    "once you can ping\n**This might be because someone unreacted to your post, so "
                    "now it doesn't have enough reacts!**\nFor feedback, use this form: https://goo.gl/forms/Pn02Vbl7WWpLzKix2")
        else:
            # If that's wrong send the user a warning.
            await ctx.author.send(
                "Somehow your command is messed up. Make sure you didn't already ping and that the number is correct!\n"
                "For feedback, use this form: https://goo.gl/forms/Pn02Vbl7WWpLzKix2")
        # Delete the message if it is not sent
        if not isinstance(ctx.message.channel, discord.DMChannel):
            await ctx.message.delete()

    @ping.error
    async def ping_error(self, ctx: discord.ext.commands.context.Context, error):
        """
        Error handler for the ping command
        :param ctx: Context
        :param error: Error message
        :return: nothing
        """
        # If the message can't be found, send the user a warning
        if isinstance(error, commands.BadArgument):
            await ctx.author.send(f"Couldn't find that message. Make sure to copy and paste the command I sent you!\n"
                                  f"For feedback, use this form: https://goo.gl/forms/Pn02Vbl7WWpLzKix2")
        else:
            # For other errors, send a generic message and log the error
            await ctx.author.send(f"Something went wrong... Sorry about that.\n"
                                  f"For feedback, use this form: https://goo.gl/forms/Pn02Vbl7WWpLzKix2")
            self.log.warning(f"{ctx.author.display_name} tried to run ping but ran into this error: {error}")
