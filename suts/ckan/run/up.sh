#!/bin/bash
set -x
export UID
docker image prune -f
docker volume prune -f
docker-compose rm -f
docker-compose pull
docker-compose up --force-recreate --build -d
