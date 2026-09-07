"""健康检查 + 基础路由测试"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_send_code():
    resp = client.post("/api/send-code", json={"phone": "13800138000"})
    assert resp.status_code == 200
    assert "dev_code" in resp.json()
