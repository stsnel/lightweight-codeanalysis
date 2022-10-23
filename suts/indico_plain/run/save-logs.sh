#!/bin/bash
cd "$(dirname "$0")"
docker logs indicocontainers_indico-web_1 >& indico.log
