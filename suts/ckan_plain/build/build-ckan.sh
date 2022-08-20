#!/bin/bash

set -x
set -e

if [ ! -d ckan ]
then git clone https://github.com/stsnel/ckan.git
fi

cd ckan
git checkout ckan-2.9.3
cp ../docker-compose-build.yml contrib/docker/docker-compose.yml
cp ../ckan-entrypoint.sh contrib/docker/ckan-entrypoint.sh
cp ../Dockerfile .
docker build . --no-cache -t 378672356020.dkr.ecr.us-east-1.amazonaws.com/ckan_plain
