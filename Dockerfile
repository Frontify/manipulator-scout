FROM python:3.14 AS build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./src ./pyproject.toml ./uv.lock /app/
WORKDIR /app

RUN uv build --clear --wheel && bash -c "pip3 install dist/*.whl"

FROM python:3.14 AS runtime
ARG ARG_PORT=41000

COPY --from=build "/usr/local/lib/python3.14/site-packages" "/usr/local/lib/python3.14/site-packages"
COPY --from=build "/usr/local/bin/uvicorn" "/usr/local/bin/uvicorn"

EXPOSE ${ARG_PORT}
COPY --chmod=755 <<EOT /entrypoint.sh
#!/bin/bash
set -e
uvicorn --port=${ARG_PORT} manipulator_scout:app
EOT

ENTRYPOINT ["/entrypoint.sh"]
