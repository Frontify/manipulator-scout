FROM python:3.14 AS build
ARG ARG_PACKAGE_VERSION="0.0.0"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./src /app/src
COPY ./pyproject.toml ./uv.lock /app/
WORKDIR /app

RUN SETUPTOOLS_SCM_PRETEND_VERSION="${ARG_PACKAGE_VERSION}" \
    uv build --clear --wheel && bash -c "pip install dist/*.whl"

FROM python:3.14 AS runtime
ARG ARG_PORT=41000

COPY --from=build "/usr/local/lib/python3.14/site-packages" "/usr/local/lib/python3.14/site-packages"
COPY --from=build "/usr/local/bin/uvicorn" "/usr/local/bin/uvicorn"

EXPOSE ${ARG_PORT}
ENV MANIPULATOR_SCOUT_PORT=${ARG_PORT}
COPY --chmod=755 <<EOT /entrypoint.sh
#!/bin/bash
set -e
uvicorn \\
    --host="0.0.0.0" \\
    --port="\${MANIPULATOR_SCOUT_PORT}" \\
    manipulator_scout:app
EOT

ENTRYPOINT ["/entrypoint.sh"]
