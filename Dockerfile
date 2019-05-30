FROM python:3
RUN pip3 install discord.py
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY PugHelpBot/ /usr/src/bot/PugHelpBot/
COPY config.json /usr/src/bot/
ENTRYPOINT ["python3", "-m", "PugHelpBot"]
