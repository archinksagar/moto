"""Test different server responses."""
from moto import mock_backup
import moto.server as server

@mock_backup
def test_backup_list():
    backend = server.create_backend_app("backup")
    test_client = backend.test_client()

    resp = test_client.get("/")

    assert resp.status_code == 200
    assert "?" in str(resp.data)