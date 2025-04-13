#!/bin/bash

docker build --platform=linux/amd64 -t telegram-server -f Dockerfile.telegram ./
docker image tag telegram-server 192.168.178.35:5000/pigion/telegram-server:latest
docker push 192.168.178.35:5000/pigion/telegram-server:latest