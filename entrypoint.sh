#!/bin/sh
set -e

echo "Starting nginx..."
nginx -g 'daemon off;' &

echo "Starting uWSGI..."
exec uwsgi --ini /app/0x0.ini
