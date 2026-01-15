import typing
import os
import httpx
import pytest
import manipulator_scout
from fastapi.testclient import TestClient
import contextlib
from types import TracebackType


ENV_MANIPULATOR_SCOUT_URL = "MANIPULATOR_SCOUT_URL"


class ClientContext(contextlib.AbstractContextManager[httpx.Client]):
    @staticmethod
    def all() -> typing.Iterable:
        if url := os.getenv(ENV_MANIPULATOR_SCOUT_URL, None):
            client = httpx.Client(base_url=url)
            return (pytest.param(ClientContext(client), id="SPAWNED"),)
        return (
            pytest.param(ClientContext(TestClient(manipulator_scout.app)), id="TEST"),
            pytest.param(
                None, marks=pytest.mark.skipif(not url, reason=f"{ENV_MANIPULATOR_SCOUT_URL} not set"), id="SPAWNED"
            ),
        )

    def __init__(self, client: httpx.Client) -> None:
        self._client = client
        self._stack = contextlib.ExitStack()

    def __enter__(self) -> httpx.Client:
        return self._stack.enter_context(self._client)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return self._stack.__exit__(exc_type, exc_value, traceback)
