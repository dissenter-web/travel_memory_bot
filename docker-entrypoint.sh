#!/bin/sh
set -eu

mkdir -p /app/data/photos

if [ ! -f /app/data/phrases.json ]; then
    cp /app/default-data/phrases.json /app/data/phrases.json
fi

exec "$@"
