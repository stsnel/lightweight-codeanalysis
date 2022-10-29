#!/bin/bash

set -x

if [ -f "strings.json" ]
then rm "strings.json"
fi

docker cp run_indico-web_1:/tmp/strings.json .
