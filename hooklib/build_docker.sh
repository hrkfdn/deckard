#!/bin/sh

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

MYUID=$(id -u)
MYGID=$(id -g)

echo "[+] Building Docker image for build environment"
docker build -t deckard-ndk $SCRIPTPATH

echo "[+] Running ndk-build"
docker run --rm -u "$MYUID:$MYGID" -v $SCRIPTPATH:/src -w /src deckard-ndk ndk-build
