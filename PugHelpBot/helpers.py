import discord
import discord.ext
import json
from datetime import datetime, timedelta


class Config:
    # Object for holding info from the config.json
    # Reads config.json and sets it's values from there
    def __init__(self):
        try:
            with open("config.json", "r") as config_file:
                self.config_object = json.load(config_file)
        except FileNotFoundError:
            raise SystemExit("Could not find config")
        self.token = self.config_object["token"]
        self.allowed_channels = self.config_object["allowed_channels"]
        self.min_players = self.config_object["min_players"]
        self.bot_prefix = self.config_object["bot_prefix"]
        self.mod_roles = self.config_object["mod_roles"]
        self.advanced_roles = self.config_object["advanced_roles"]

    def set_min_players(self, min_players: int):
        self.min_players = min_players


class PingStatus:
    """
    Object that stores the current status of message, if they were pinged, and if they were notified for.
    Also has method to purge old messages from it.
    """

    def __init__(self):
        self.already_notified = []
        self.already_pinged = []

    def add_already_notified(self, message: int):
        self.already_notified.append({"date": datetime.now(), "id": message})

    def add_already_pinged(self, message: int):
        self.already_pinged.append({"date": datetime.now(), "id": message})

    def get_already_notified_simple(self):
        return [message["id"] for message in self.already_notified]

    def get_already_pinged_simple(self):
        return [message["id"] for message in self.already_pinged]

    def purge(self):
        for message in self.already_notified:
            if message["date"] < datetime.now() - timedelta(hours=12):
                self.already_notified.remove(message)

        for message in self.already_pinged:
            if message["date"] < datetime.now() - timedelta(hours=12):
                self.already_notified.remove(message)


async def send_ping(message: discord.Message, users_to_mention: list):
    """
    Create an embed with info and post it in the channel of the original message
    :param message: The original message
    :param users_to_mention: List of users to mention
    :return: Nothing
    """
    # Create an embed
    embed = discord.Embed(title=f"{message.author.display_name} said:", description=f"{message.content}")
    # Create a string of all the users separated by \n
    users_string = "\n".join(user.mention for user in users_to_mention)
    # Post the message
    await message.channel.send(embed=embed)
    await message.channel.send(users_string)


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


def is_mod(ctx: discord.ext.commands.context.Context, config: Config) -> bool:
    """
    Used to check if a person has one of the mod roles
    :param ctx: Context
    :param config: Config
    :return: Bool if they have the role
    """
    for role in ctx.author.roles:
        if role.name in config.mod_roles:
            return True
    return False


def is_advanced(ctx: discord.ext.commands.context.Context, config: Config) -> bool:
    """
    Used to check if a person has one of the advanced or mod roles
    :param ctx: Context
    :param config: Config
    :return: Bool if they have the role
    """
    for role in ctx.author.roles:
        if role.name in config.mod_roles:
            return True
        if role.name in config.advanced_roles:
            return True
    return False
