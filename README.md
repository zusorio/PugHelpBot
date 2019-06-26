# PUG Help Bot
This is a relatively simple discord bot written for the Elo Hell PUG discord.
If a post in the specified channels (in the config.json) reaches the minimum required reacts
the bot will DM the message writer with a command they can send to the bot. That command
then mentions all the players who reacted to that message in the channel where the original
message was sent.

# Setup and Running the Bot
The bot needs a file called config.json to run. This file can be placed above or inside the
PugHelpBot __module__ (the directory with `__init__.py` in it). As an example use
`config_example.json`, rename it and then change some of the fields (the token and webhook).


The bot needs the modules discord.py and requests. PyNaCl is installed to prevent warnings,
however it does not need to be installed to run the bot.

There is a script for automatically creating a docker container that the bot runs inside of.
__The script deletes containers so be careful before running it!__ You can also run the
bot outside of a container. It needs to be run __as a module__.


To run it as a module, go into the directory above the module, then run
`python3 -m PugHelpBot`.


If you want to run the bot inside of pycharm, here's a file of the config that I use.

![Config for Pycharm](https://i.imgur.com/rT4CvWS.png)