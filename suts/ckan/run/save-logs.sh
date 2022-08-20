#!/bin/bash
cd "$(dirname "$0")"
docker logs ckan >& ckan.log
RND=$(expr $RANDOM % 5)
#for n in $(seq 1 $RND)
#do echo "Exception occurred" >> ckan.log
#done
