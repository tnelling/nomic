#!/bin/bash

# THIS FILE IS OUT OF BOUNDS

set -e  # die on failure

if [ -z "$TRAVIS_REPO_SLUG" ]; then
  echo "Missing repo."
  exit 1
fi

if [ -z "$TRAVIS_PULL_REQUEST" ]; then
  echo "Missing PR number."
  exit 1
fi

if [ -d tmp-nomic-master ]; then
  rm -rf tmp-nomic-master
fi

git clone --depth=1 https://github.com/${TRAVIS_REPO_SLUG}.git tmp-nomic-master

cd tmp-nomic-master

python3 validate.py

cd ..

rm -rf tmp-nomic-master
