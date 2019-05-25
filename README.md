# PUG Help Bot
This is a relatively simple discord bot written for the Elo Hell PUG discord.
If a post in the specified channels (in the config.json) reaches the minimum required reacts
the bot will DM the message writer with a command they can send to the bot. That command
then mentions all the players who reacted to that message in the channel where the original
message was sent.
# Setup
Create a file called config.json similar to the config_example.json. Install discord.py
and use python3.