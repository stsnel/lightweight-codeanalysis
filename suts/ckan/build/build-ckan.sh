#!/bin/bash
git clone https://github.com/ckan/ckan.git
cd ckan
git checkout 872b45a826fe81cf334c211eabe992b8082512cd
cp ../docker-compose-build.yml contrib/docker/docker-compose.yml

