"""HTTP layer: endpoints, status codes, and error mapping.

Uses a bare FastAPI app (routers + exception handler, no lifespan) so no real
network or Roomspot login is involved; platform clients are stubbed via
dependency_overrides.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from notbehomeless.api.dependencies import (
    get_auto_signer_manager,
    get_roomspot,
    get_roomspot_service,
    get_session,
)
from notbehomeless.api.routers import health, rooms, signers
from notbehomeless.factory.exceptions_factory import init_exceptions_handler
from notbehomeless.service.auto_signer_manager import AutoSignerManager
from notbehomeless.websites.roomspot.service import RoomspotService

from tests.conftest import SimApi


def build_app(api: SimApi, manager: AutoSignerManager | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(health.router)
    app.include_router(rooms.router)
    app.include_router(signers.router)
    init_exceptions_handler(app)

    app.dependency_overrides[get_session] = lambda: object()
    app.dependency_overrides[get_roomspot] = lambda: api
    app.dependency_overrides[get_roomspot_service] = lambda: RoomspotService(api)
    app.dependency_overrides[get_auto_signer_manager] = lambda: manager or AutoSignerManager()
    return app


@pytest.fixture
def rooms_client(make_room):
    api = SimApi(rooms=[
        make_room(room_id=1, price=400, private_kitchen=True),
        make_room(room_id=2, price=900),
        make_room(room_id=3, price=650, action="remove"),
    ])
    return TestClient(build_app(api)), api


def test_health():
    client = TestClient(build_app(SimApi()))
    assert client.get("/health").json() == {"status": "ok"}


def test_list_rooms_no_filter_returns_all(rooms_client):
    client, _ = rooms_client
    body = client.get("/rooms").json()
    assert [r["room_id"] for r in body] == [1, 2, 3]


def test_list_rooms_filters_via_query(rooms_client):
    client, _ = rooms_client
    assert [r["room_id"] for r in client.get("/rooms?max_price=700").json()] == [1, 3]
    assert [r["room_id"] for r in client.get("/rooms?kitchen=true").json()] == [1]


def test_react_success(rooms_client):
    client, api = rooms_client
    response = client.post("/rooms/1/react", json={"action": "add"})
    assert response.status_code == 200
    assert response.json()["status"] == "add"
    assert api.signed == [1]


def test_react_unknown_room_404(rooms_client):
    client, _ = rooms_client
    response = client.post("/rooms/999/react", json={"action": "add"})
    assert response.status_code == 404


def test_react_action_mismatch_409(rooms_client):
    client, _ = rooms_client
    # room 3 offers "remove", requesting "add" must be rejected
    response = client.post("/rooms/3/react", json={"action": "add"})
    assert response.status_code == 409


def test_react_invalid_action_422(rooms_client):
    client, _ = rooms_client
    assert client.post("/rooms/1/react", json={"action": "sit"}).status_code == 422


def test_react_upstream_failure_502(make_room):
    api = SimApi(rooms=[make_room(room_id=1)], fail_sign=True)
    client = TestClient(build_app(api))
    response = client.post("/rooms/1/react", json={"action": "add"})
    assert response.status_code == 502


def test_signer_lifecycle(make_room):
    manager = AutoSignerManager()
    app = build_app(SimApi(rooms=[make_room()]), manager)

    # context manager keeps one event loop across requests, as uvicorn does
    with TestClient(app) as client:
        assert client.post("/signers/roomspot?period_seconds=5").status_code == 201
        assert client.get("/signers").json()[0]["running"] is True
        assert client.post("/signers/roomspot").status_code == 409
        assert client.delete("/signers/roomspot").status_code == 200
        assert client.delete("/signers/roomspot").status_code == 404
