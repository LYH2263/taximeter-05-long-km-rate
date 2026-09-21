import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app import db, seed  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "http.db")
    seed.init_db()
    from app.main import app
    return TestClient(app)


def test_api_crud_and_conflict(client):
    assert client.get("/api/long-km-rates").json() == {"items": []}
    r = client.post("/api/long-km-rates", json={"label": "规则甲", "start_km": 10, "per_km": 3.5, "active": True})
    assert r.status_code == 201
    rid = r.json()["id"]

    bad = client.post("/api/long-km-rates", json={"label": "规则乙", "start_km": 12, "per_km": 4.0, "active": True})
    assert bad.status_code == 400
    assert "规则甲" in bad.json()["detail"] and "规则乙" in bad.json()["detail"]

    invalid = client.post("/api/long-km-rates", json={"label": "规则丙", "start_km": 3, "per_km": 0, "active": False})
    assert invalid.status_code == 422  # schema gt=0 先拦 per_km

    r2 = client.put(f"/api/long-km-rates/{rid}", json={"label": "规则甲改", "start_km": 11, "per_km": 4.0, "active": True})
    assert r2.status_code == 200 and r2.json()["label"] == "规则甲改"

    d = client.post(f"/api/long-km-rates/{rid}/deactivate")
    assert d.status_code == 200 and d.json()["active"] == 0
    assert client.post("/api/long-km-rates/999/deactivate").status_code == 404


def test_api_fare_breakdown(client):
    client.post("/api/long-km-rates", json={"label": "规则甲", "start_km": 10, "per_km": 3.5, "active": True})
    r = client.post("/api/fare", json={"distance_km": 18, "slow_min": 12, "night": False, "persist": False})
    body = r.json()
    assert body["mileage"] == 17.5 and body["long_mileage"] == 28.0 and body["total"] == 66.1
