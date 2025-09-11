#/bin/sh
USER="$(whoami)"
echo USER=$USER >.env
echo UID=$(id -u "$USER") >>.env
echo GID=$(id -g "$USER") >>.env
echo GIT_ROOT=$(git rev-parse --show-toplevel) >>.env
