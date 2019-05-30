#!/usr/bin/env bash

cd /home/tobi/PugHelpBot
git pull
docker stop $(docker ps -f "ancestor=pug-help-bot" -q -a)
docker rm $(docker ps -f "ancestor=pug-help-bot" -q -a)
docker rmi -f pug-help-bot
docker build -t pug-help-bot .
docker run -d pug-help-bot
