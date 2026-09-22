import pytest

from fastapi.testclient import (
    TestClient
)

from app.main import app

from app.core.session_store import (
    session_store
)


@pytest.fixture
def client():

    session_store.clear()

    with TestClient(app) as test_client:
        yield test_client

    session_store.clear()