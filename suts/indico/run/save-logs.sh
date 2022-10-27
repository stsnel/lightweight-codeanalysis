#!/bin/bash
cd "$(dirname "$0")"
docker logs run_indico-web_1 >& indico.log
