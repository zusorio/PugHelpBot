from ..helpers import Config, is_mod
import logging
import discord
from discord.ext import commands


class AdminTools(commands.Cog):
    """Cog for admin commands like change_min_reacts"""
    def __init__(self, bot: commands.Bot, log: logging.Logger, config: Config):
        self.bot = bot
        self.log = log
        self.config = config

        self.log.info("Loaded Cog AdminTools")

    @commands.command()
    async def change_min_reacts(self, ctx: discord.ext.commands.context.Context, min_reacts: int):
        """Change minimum required reacts"""
        if is_mod(ctx, self.config):
            self.config.set_min_players(min_reacts)
            await ctx.author.send(f"Set the minimum amount of reacts to {min_reacts}")
        else:
            raise commands.CheckFailure

    @change_min_reacts.error
    async def change_min_reacts_error(self, ctx: discord.ext.commands.context.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send("Sorry, something went wrong... You don't have permission to do that!")
        else:
            await ctx.author.send(error)
