#!/bin/bash -e

if [ -z "$1" ]; then
    image="manipulator_scout:latest"
else
    image="$1"
fi

port=50000

run_container() {
    docker run \
        -it \
        --rm \
        --detach \
        --publish "${port}:${port}" \
        --env "MANIPULATOR_SCOUT_PORT=${port}" \
        "${image}"
}

container_id="$(run_container)"
on_exit() {
    docker stop "${container_id}"
}
trap on_exit EXIT

export MANIPULATOR_SCOUT_URL="http://localhost:${port}"
uv run pytest -m "system"
