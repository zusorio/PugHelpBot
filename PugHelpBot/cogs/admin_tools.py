from ..helpers import Config, is_mod, PingStatus
import logging
import discord
from discord.ext import commands, tasks


class AdminTools(commands.Cog):
    """Cog for admin commands like change_min_reacts"""

    def __init__(self, bot: commands.Bot, log: logging.Logger, config: Config, ping_status: PingStatus):
        self.bot = bot
        self.log = log
        self.config = config
        self.ping_status = ping_status

        self.log.info("Loaded Cog AdminTools")
        self.auto_purge_message_cache.start()

    @commands.command()
    async def change_min_reacts(self, ctx: discord.ext.commands.context.Context, min_reacts: int):
        """Change minimum required reacts"""
        if is_mod(ctx, self.config):
            self.config.set_min_players(min_reacts)
            self.log.warning(f"{ctx.author.display_name} set the minimum amount of reacts to {min_reacts}")
            await ctx.send(f"Set the minimum amount of reacts to {min_reacts}")
        else:
            raise commands.CheckFailure

    @change_min_reacts.error
    async def change_min_reacts_error(self, ctx: discord.ext.commands.context.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send("Sorry, something went wrong... You don't have permission to do that!")
            self.log.warning(f"{ctx.author.display_name} tried to run change_min_reacts but did not have permission.")
        else:
            await ctx.author.send(error)
            self.log.warning(
                f"{ctx.author.display_name} tried to run change_min_reacts but ran into this error: {error}")

    @commands.command()
    async def echo(self, ctx: discord.ext.commands.context.Context, channel: discord.TextChannel,
                   message: discord.Message):
        """Repeat a message into another channel. For announcements."""
        if is_mod(ctx, self.config):
            await channel.send(message.content)
            await ctx.send("Done!")
        else:
            raise commands.CheckFailure

    @echo.error
    async def echo_error(self, ctx: discord.ext.commands.context.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send("Sorry, something went wrong... You don't have permission to do that!")
            self.log.warning(f"{ctx.author.display_name} tried to run echo but did not have permission.")
        elif isinstance(error, commands.BadArgument):
            await ctx.author.send("The arguments for the command are a message ID and then a channel name"
                                  " For just sending text use send instead.")
        else:
            await ctx.author.send(error)
            self.log.warning(f"{ctx.author.display_name} tried to run echo but ran into this error: {error}")

    @commands.command()
    async def say(self, ctx: discord.ext.commands.context.Context, channel: discord.TextChannel, *, message: str):
        """Post a message to a channel. For announcements."""
        if is_mod(ctx, self.config):
            await channel.send(message)
        else:
            raise commands.CheckFailure

    @say.error
    async def say_error(self, ctx: discord.ext.commands.context.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send("Sorry, something went wrong... You don't have permission to do that!")
            self.log.warning(f"{ctx.author.display_name} tried to run echo but did not have permission.")
        elif isinstance(error, commands.BadArgument):
            await ctx.author.send("The arguments for the command are a message ID and then a channel name"
                                  " For just sending text use send instead.")
        else:
            await ctx.author.send(error)
            self.log.warning(f"{ctx.author.display_name} tried to run echo but ran into this error: {error}")

    @commands.command()
    async def purge_old_message_cache(self, ctx: discord.ext.commands.context.Context):
        if is_mod(ctx, self.config):
            amount_cleared = self.ping_status.purge()
            await ctx.send(f"Done! {amount_cleared} removed.")
            self.log.warning(f"{ctx.author.display_name} cleared the old message cache. {amount_cleared} were removed")

    @purge_old_message_cache.error
    async def purge_old_message_cache_error(self, ctx: discord.ext.commands.context.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send("Sorry, something went wrong... You don't have permission to do that!")
            self.log.warning(f"{ctx.author.display_name} tried to run echo but did not have permission.")
        else:
            await ctx.author.send(error)
            self.log.warning(f"{ctx.author.display_name} tried to run echo but ran into this error: {error}")

    @tasks.loop(hours=1)
    async def auto_purge_message_cache(self):
        count = self.ping_status.purge()
        if count != 0:
            self.log.warning(f"Purged message cache ({count} messages)")
