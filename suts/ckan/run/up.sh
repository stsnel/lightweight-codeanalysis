#!/bin/bash
set -x
export UID
docker container prune -f
docker image prune -f
docker volume prune -f
docker-compose pull
docker-compose up --force-recreate --build -d
