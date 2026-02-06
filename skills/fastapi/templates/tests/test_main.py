# tests/test_main.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_item(client):
    response = await client.post("/items", json={"name": "Test", "price": 9.99})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
