from ..helpers import Config, PingStatus, time_in_range, is_advanced
import logging
import discord
from discord.ext import commands
from datetime import datetime, timedelta


class PingUnofficials(commands.Cog):
    """Cog to ping unofficials. Requires pug vet or higher"""

    def __init__(self, bot: commands.Bot, log: logging.Logger, config: Config, ping_status: PingStatus):
        self.bot = bot
        self.log = log
        self.config = config
        self.ping_status = ping_status

        self.log.info("Loaded Cog PingUnofficials")

    def check_message_allowed(self, message: discord.Message):
        # Get the channel region
        region_info = self.config.get_region_from_channel_name(message.channel.name)
        # Check that it's the correct time
        if not time_in_range(region_info["allow_start_utc"], region_info["allow_end_utc"], datetime.utcnow().time()):
            return False
        if not is_advanced(message, self.config):
            return False
        if not region_info["last_ping"]:
            return True
        elif datetime.utcnow() >= region_info["last_ping"] + timedelta(hours=self.config.unofficials_ping.cooldown):
            return True


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        # Make sure we don't react to the bot
        if user != self.bot.user:
            # Make sure the reacts is the check, the reactant is the user and that the reaction is in the channel for pinging
            if reaction.emoji == "✅" and user == reaction.message.author and reaction.message.channel.name in self.config.get_ping_channels() and self.check_message_allowed(reaction.message):
                # Get the channel we need to ping from the config
                target_channel: discord.TextChannel = discord.utils.get(reaction.message.guild.channels, name=self.config.get_channel_from_ping_channel(reaction.message.channel.name))
                # Get the unofficial role from the server with config help
                target_role = discord.utils.get(reaction.message.guild.roles, name=self.config.unofficials_ping.role_name)

                # Clear all reacts on the original message
                await reaction.message.clear_reactions()
                # Mention the role
                await target_channel.send(f"{target_role.mention}")
                # Create and send the embed
                original_message_embed = discord.Embed(title=f"{reaction.message.author.display_name}:", color=discord.Colour.green(), description=reaction.message.content)
                await target_channel.send(embed=original_message_embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Check that message is from user and user has perms
        if message.author == self.bot.user:
            return
        # If the message is in one of the channels add a check react
        if message.channel.name in self.config.get_ping_channels():
            if self.check_message_allowed(message):
                await message.add_reaction("✅")
            else:
                await message.channel.send("Sorry, you can't ping right now!")
                await message.add_reaction("❌")
