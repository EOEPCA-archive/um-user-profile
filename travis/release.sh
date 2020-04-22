#!/usr/bin/env bash

# fail fast settings from https://dougrichardson.org/2018/08/03/fail-fast-bash-scripting.html
set -euov pipefail

# Check presence of environment variables
TRAVIS_BUILD_NUMBER="${TRAVIS_BUILD_NUMBER:-0}"
buildTag=travis_$TRAVIS_BUILD_NUMBER # We use a temporary build number for tagging, since this is a transient artefact

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker pull eoepca/$1:$buildTag  # have to pull locally in order to tag as a release

# Tag and push as a Release
docker tag eoepca/$1:$buildTag eoepca/$1:release_$TRAVIS_BUILD_NUMBER
docker push eoepca/$1:release_$TRAVIS_BUILD_NUMBER

# Tag and push as `latest`
docker tag eoepca/$1:$buildTag eoepca/$1:latest
docker push eoepca/$1:latest
