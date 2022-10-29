#!/bin/bash
set -x
docker exec run_indico-web_1 touch /tmp/strings.json
docker exec run_indico-web_1 rm /tmp/strings.json
docker exec run_indico-web_1 /usr/local/bin/extract-strings.py $1 /tmp/strings.json
