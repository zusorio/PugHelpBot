from ..helpers import Config, get_unique_message_react_users, PingStatus
from datetime import datetime, timedelta
import logging
import discord
from discord.ext import commands, tasks


class ChannelClean(commands.Cog):
    def __init__(self, bot: commands.Bot, log: logging.Logger, config: Config, ping_status: PingStatus):
        self.bot = bot
        self.log = log
        self.config = config
        self.ping_status = ping_status

        self.log.info("Loaded Cog ChannelClean")

    async def delete_message(self, message: discord.Message):
        await message.delete()
        self.log.warning(f"Deleted message {message.content} by {message.author.display_name} in {message.channel.name}")

    @tasks.loop(minutes=30)
    async def delete_old_messages(self, ctx: discord.ext.commands.context.Context):
        # TODO: Make this hours
        # Loop over all channels in the clean_channel config parameter
        for channel in self.config.clean_channels:
            # Loop over all messages in the channel during the correct time
            async for message in discord.utils.get(self.bot.get_all_channels(), name=channel).history(before=datetime.utcnow() - timedelta(minutes=self.config.delete_after_hours), after=datetime.utcnow() - timedelta(hours=24)):
                message_react_count = len(get_unique_message_react_users(message))
                # If the message has enough reacts to have notified
                if message_react_count >= self.config.min_reacts:
                    # And it was pinged for
                    if message.id in self.ping_status.already_pinged:
                        # Delete it
                        await self.delete_message(message)
                    # TODO: If it wasn't pinged for what to do?
                    else:
                        pass
                # If it didn't have enough reacts but has enough to not be deleted
                elif message_react_count >= self.config.min_reacts - self.config.avoid_delete_react_threshold:
                    # TODO: What to do here
                    pass
                # If it didn't hit the threshold either just delete it`
                else:
                    await self.delete_message(message)