import json
import discord
from discord.ext import commands


class Config:
    # Object for holding info from the config.json
    # Reads config.json and sets it's values from there
    def __init__(self):
        with open("config.json", "r") as config_file:
            self.config_object = json.load(config_file)
        self.token = self.config_object["token"]
        self.allowed_channels = self.config_object["allowed_channels"]
        self.min_players = self.config_object["min_players"]
        self.bot_prefix = self.config_object["bot_prefix"]


# Create the config object and read config.json
config = Config()

# Create bot object with prefix from config
bot = commands.Bot(command_prefix=config.bot_prefix)

# Stores message id's from messages that were already used to mention people
# Prevents pinging for a message twice
already_pinged_messages = []

# Stores message id's from messages that we already told the user about
# Otherwise the user gets spammed after the min amount of reacts whenever someone reacts
already_notified_messages = []


async def get_unique_message_react_users(message: discord.Message) -> list:
    """
    Get's every user that reacted to a certain message. Merges duplicates.
    :param message: A message object from discord.py
    :return: List of discord User Objects
    """
    unique_users = []
    # Iterate over all reaction types (So every emoji) on a message
    for reaction_type in message.reactions:
        # Iterate over every reaction from that type
        async for user in reaction_type.users():
            # If the user isn't already in our list add them
            if user not in unique_users:
                unique_users.append(user)
    return unique_users


@bot.event
async def on_ready():
    # Set rich presence and inform us once the bot is ready
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"PUGS (Prefix {config.bot_prefix})"))
    print("Logged in")


@bot.event
async def on_reaction_add(reaction: discord.Reaction, _):
    # If the reaction is on a message in the specified channels and wasn't pinged and notified for
    if reaction.message.channel.name in config.allowed_channels and reaction.message.id not in already_notified_messages and reaction.message.id not in already_pinged_messages:
        # Get all unique users that reacted
        unique_reacts = await get_unique_message_react_users(reaction.message)
        # If there are the minimum of required reacts
        if len(unique_reacts) >= config.min_players:
            # Send the user instructions on how to mention all of the reactants
            # The command the user is told to use is (prefix)ping MESSAGE_ID_OF_ORIGINAL_POST
            await reaction.message.author.send(
                f"Your LFP Post reached the minimum of {config.min_players}"
                f"reacts!\nReply with `{config.bot_prefix}ping {reaction.message.id}` "
                f"__**in this DM**__  to ping the people that want to join!")
            # Mark the message to not notify the user again
            already_notified_messages.append(reaction.message.id)


@bot.command()
async def ping(ctx: discord.ext.commands.context.Context, message: discord.Message):
    """
    A command using discord.py's bot framework. Used to mention the people that reacted to the message.
    :param ctx: Discord context
    :param message: The message ID of the message to ping for. The user get's this sent in the command they are told to use.
    :return: Nothing
    """
    # Check that we are being sent the command via DM
    if isinstance(ctx.message.channel, discord.DMChannel):
        # Make sure that the message is in a correct channel and that we haven't pinged for it yet
        if message.channel.name in config.allowed_channels and message.id not in already_pinged_messages:
            # Get all the users we need the mention for that message
            users_to_mention = await get_unique_message_react_users(message)
            # Make sure there are actually enough users for a ping
            if len(users_to_mention) >= config.min_players:
                # If everything is OK, mention all the users in a post in the original channel, separated by newlines
                await message.channel.send("\n".join(user.mention for user in users_to_mention))
                # Add the message to the already_pinged list so that the user doesn't ping for the same message twice
                already_pinged_messages.append(message.id)
                # Tell the user that everything is done.
                await ctx.send(
                    "I mentioned all the people who reacted to your post in that channel. Make sure to put a message "
                    "there telling them which lobby to join!")
            else:
                # Warn the user that there are not enough reactions.
                await ctx.send(
                    "The message doesn't have enough reacts yet! Don't try and write commands manually. I'll tell you "
                    "once you can ping.")
        else:
            # If that's wrong send the user a warning.
            await ctx.send(
                "Somehow your command is messed up. Make sure you didn't already ping and that the number is correct!")
    else:
        # If not in a DM, warn the User and delete the message
        await ctx.author.send("Please use my commands via DM only!")
        # TODO: Make sure that the permissions are OK and that staff are OK with this
        await ctx.message.delete()


@ping.error
async def ping_error(ctx: discord.ext.commands.context.Context, error):
    """
    Error handler for the ping command
    :param ctx: Context
    :param error: Error message
    :return: nothing
    """
    # If the message can't be found, send the user a warning
    if isinstance(error, commands.BadArgument):
        await ctx.send("Couldn't find that message. Make sure to copy and paste the command I sent you!")
    else:
        # For other errors, send a generic message and log the error
        await ctx.send("Something went wrong... Sorry about that.")

        print(error)


@bot.command()
async def mod_ping(ctx: discord.ext.commands.context.Context, message: discord.Message):
    # Bypasses all checks and just pings for any message. Just give it any message ID
    # TODO: Make this check for a staff role before running
    users_to_mention = await get_unique_message_react_users(message)
    await message.channel.send("\n".join(user.mention for user in users_to_mention))
    # Tell the user that everything is done.
    await ctx.send(
        "I mentioned all the people who reacted to your post in that channel. Make sure to put a message "
        "there telling them which lobby to join!")
    # Add the message to the already_pinged and already_notified list
    # Note: this does not prevent repeat staff pings
    already_pinged_messages.append(message.id)
    already_notified_messages.append(message.id)


@mod_ping.error
async def mod_ping_error(ctx: discord.ext.commands.context.Context, error):
    await ctx.send(error)
    print(error)


@bot.command()
async def change_min_reacts(ctx: discord.ext.commands.context.Context, min_reacts: int):
    # TODO: Make this check for a staff role before running
    config.min_players = min_reacts
    await ctx.send(f"Set the minimum amount of reacts to {min_reacts}")


# Run the bot
bot.run(config.token)
