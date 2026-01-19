#!/bin/bash -e

CI_DIR="$(dirname "$0")"

if [ -z "$1" ]; then
    image_tag="$(git describe --tag || echo "0.0.0")"
else
    image_tag="$1"
fi

uv sync --group ci
package_version="$(uv --quiet run python -m setuptools_scm)"

docker build "${CI_DIR}/.." \
    --build-arg "ARG_PACKAGE_VERSION=${package_version}" \
    --tag manipulator_scout:"${image_tag}"
