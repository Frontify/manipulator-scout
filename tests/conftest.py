import pathlib

import pytest


TESTS_PATH = pathlib.Path(__file__).parent


@pytest.fixture(name="logs_path")
def logs_path_fixture():
    return TESTS_PATH.parent / "data" / "logs"
