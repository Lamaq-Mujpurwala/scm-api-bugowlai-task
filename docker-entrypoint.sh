#!/bin/sh

# This script is the entrypoint for the Docker container.
# It ensures that the database is up-to-date before starting the application.

# The 'exec "$@"' command at the end is important. It replaces the shell
# process with the command you pass to the script. This is a best practice
# for Docker entrypoints, as it allows signals (like SIGTERM for stopping
# the container) to be passed correctly to the application.

echo "Running database migrations..."
alembic -c /alembic.ini upgrade head

echo "Starting application..."
exec "$@"
