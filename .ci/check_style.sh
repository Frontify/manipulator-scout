#!/bin/bash -e
uv run ruff format --check
uv run ruff check
