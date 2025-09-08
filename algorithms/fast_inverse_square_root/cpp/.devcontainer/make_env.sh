#/bin/sh
echo USER=$(whoami) >.env
echo UID=$(id -u "$USER") >>.env
echo GID=$(id -g "$USER") >>.env
echo GIT_ROOT=$(git rev-parse --show-toplevel) >>.env
