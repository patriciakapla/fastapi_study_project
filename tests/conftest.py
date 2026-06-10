import pytest
from fastapi.testclient import TestClient

from fastapi_study_project.app import app


@pytest.fixture
def client():
    return TestClient(app)
