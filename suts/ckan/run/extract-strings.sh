#!/bin/bash
set -x
docker exec ckan touch /tmp/strings.json
docker exec ckan rm /tmp/strings.json
docker exec ckan /usr/local/bin/extract-strings.py $1 /tmp/strings.json
