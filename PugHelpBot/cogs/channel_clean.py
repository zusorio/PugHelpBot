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

        self.channels_to_check = None
        self.initialize.start()
        self.log.info("Loaded Cog ChannelClean")

    @tasks.loop(seconds=1, count=1)
    async def initialize(self):
        # wait until bot is fully ready
        await self.bot.wait_until_ready()
        self.channels_to_check = [discord.utils.get(self.bot.get_all_channels(), name=channel)
                                  for channel in self.config.clean_channels]
        self.clean_up_channel.start()
        self.log.info("CleanChannel is fully ready")

    async def delete_message(self, message: discord.Message):
        await message.delete()
        self.log.warning(
            f"Deleted message {message.content if message.content else 'no displayable content'} by {message.author.display_name} in {message.channel.name}")

    @tasks.loop(minutes=5)
    async def clean_up_channel(self):
        # Find the times between we want to check messages
        delete_hours_ago_time = datetime.utcnow() - timedelta(hours=self.config.delete_after_hours)
        day_ago = datetime.utcnow() - timedelta(hours=24)

        for channel in self.channels_to_check:  # For each channel obj in channels to check

            # Loop over all messages in the channel during the correct time
            async for message in channel.history(before=delete_hours_ago_time, after=day_ago):
                unique_reacts = await get_unique_message_react_users(message)
                message_react_count = len(unique_reacts)

                # If the message has enough reacts to have notified
                if message_react_count >= self.config.min_reacts:
                    # If it was pinged for delete it
                    if message.id in self.ping_status.already_pinged:
                        await self.delete_message(message)
                    # Else ping for it and delete the original message
                    else:
                        await send_ping(message, unique_reacts)
                        self.ping_status.add_already_pinged(message.id)
                        await self.delete_message(message)

                # If it didn't have enough reacts but has enough to not be deleted ping for it.
                elif message_react_count >= self.config.min_reacts - self.config.avoid_delete_react_threshold:
                    # If it was pinged for delete it
                    if message.id in self.ping_status.already_pinged:
                        await self.delete_message(message)
                    # Ping for it then delete original
                    else:
                        await send_ping(message, unique_reacts)
                        self.ping_status.add_already_pinged(message.id)
                        await self.delete_message(message)

                # If it didn't hit the threshold either just delete it
                else:
                    await self.delete_message(message)
