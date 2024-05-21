# 
# 15/05/2024.
# 
# pytest entry.
# 
# To run all tests:
# 
# 1. venv\Scripts\python.exe -m pytest
# 2. venv\Scripts\pytest.exe
# 
# To run individual tests:
# 
# venv\Scripts\pytest.exe -m <@pytest.mark>
# 
# Valid @pytest.marks are defined in pytest.ini.
# 

import pytest

from fastapi.testclient import TestClient

from . import test_main

@pytest.fixture(scope='module')
def app():
    return test_main.app

@pytest.fixture(scope='module')
def test_client():
    with TestClient(test_main.app) as c:
        yield c
