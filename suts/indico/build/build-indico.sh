#!/bin/bash
git clone https://github.com/indico/indico-containers.git
cd indico-containers
git checkout 9fe18d04dc14d125ad2630a87216182c5adb004e
cp ../docker-compose-build.yml docker-compose.yml
cp indico.env.sample indico.env
