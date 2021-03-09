#!/usr/bin/env bash

# fail fast settings from https://dougrichardson.org/2018/08/03/fail-fast-bash-scripting.html
set -euov pipefail


# Check presence of environment variables
TRAVIS_BUILD_NUMBER="${TRAVIS_BUILD_NUMBER:-0}"

# Create a Docker image and tag it as 'travis_<build number>'
buildTag=travis_$TRAVIS_BUILD_NUMBER # We use a temporary build number for tagging, since this is a transient artefact

docker build -t eoepca/$1 .
docker tag eoepca/$1 eoepca/$1:$buildTag

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

docker push eoepca/$1:$buildTag   # defaults to docker hub EOEPCA repo

