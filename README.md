# manipulator-scout

Web API endpoint for scouting, analyzing, and interpreting runtime telemetry from `manipulator` test executions.

## Prerequisites

- `uv` (Universal Virtualenv) - [A tool for managing Python virtual environments and dependencies](https://docs.astral.sh/uv/getting-started/installation/).

## Getting Started

Install necessary dependencies:

```bash
uv sync
```

Run the API server:

```bash
uv run uvicorn manipulator_scout:app
```

Check command-line interface of `uvicorn` for additional options.

## Run Formatter

```bash
uv run ruff format
```

## Run Linter

```bash
uv run ruff check
```

## Run Tests

```bash
uv run pytest
```

Check command-line interface of `pytest` for additional options.

## Build package:

```bash
uv build --wheel
```

This will create a distributable wheel file in the `dist/` directory.
