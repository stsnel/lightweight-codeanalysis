#!/bin/bash

set -x

if [ -f "strings.json" ]
then rm "strings.json"
fi

docker cp ckan:/tmp/strings.json .
