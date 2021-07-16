#!/usr/bin/env bash

# fail fast settings from https://dougrichardson.org/2018/08/03/fail-fast-bash-scripting.html
set -euov pipefail

# Check presence of environment variables
TRAVIS_BUILD_NUMBER="${TRAVIS_BUILD_NUMBER:-0}"

buildTag=travis_$TRAVIS_BUILD_NUMBER # We use a temporary build number for tagging, since this is a transient artefact

docker run --rm -d -p $2:$3 --name $1 eoepca/$1:${buildTag} # Runs container from EOEPCA repository

sleep 15 # wait until the container is running

# INSERT BELOW THE ACCEPTANCE TEST:
#curl -s http://localhost:$2/search # trivial smoke test
