FROM python:3
RUN pip3 install discord.py
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY main.py /usr/src/bot
COPY config.json /usr/src/bot

ENTRYPOINT ["python3", "/usr/src/bot/main.py"]