from ..helpers import Config, get_unique_message_react_users, PingStatus, send_ping
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

    @tasks.loop(minutes=15)
    async def delete_old_messages(self, ctx: discord.ext.commands.context.Context):
        # Loop over all channels in the clean_channel config parameter
        for channel in self.config.clean_channels:
            # Loop over all messages in the channel during the correct time
            async for message in discord.utils.get(self.bot.get_all_channels(), name=channel).history(before=datetime.utcnow() - timedelta(hours=self.config.delete_after_hours), after=datetime.utcnow() - timedelta(hours=24)):
                message_react_count = len(get_unique_message_react_users(message))
                # If the message has enough reacts to have notified
                if message_react_count >= self.config.min_reacts:
                    # If it was pinged for delete it
                    if message.id in self.ping_status.already_pinged:
                        await self.delete_message(message)
                    # Else ping for it and delete the original message
                    else:
                        await send_ping(message, get_unique_message_react_users(message))
                        self.ping_status.add_already_pinged(message.id)
                        await self.delete_message(message)
                # If it didn't have enough reacts but has enough to not be deleted ping for it.
                elif message_react_count >= self.config.min_reacts - self.config.avoid_delete_react_threshold:
                    await send_ping(message, get_unique_message_react_users(message))
                    self.ping_status.add_already_pinged(message.id)
                    await self.delete_message(message)
                # If it didn't hit the threshold either just delete it`
                else:
                    await self.delete_message(message)
