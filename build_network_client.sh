#!/bin/bash

docker build --platform=linux/amd64 -t pigion-client ./ 
docker image tag pigion-client 192.168.178.35:5000/pigion/pigion-client:latest
docker push 192.168.178.35:5000/pigion/pigion-client:latest