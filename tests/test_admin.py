import pytest


def test_admin_can_view_all_users(client, admin_auth_header, test_user):
    """Admins should be able to list all users."""
    resp = client.get("/admin/users", headers=admin_auth_header)
    assert resp.status_code == 200
    data = resp.json()

    usernames = [u["username"] for u in data]
    assert "admin_tester" in usernames
    assert "tester" in usernames


def test_non_admin_cannot_access_admin_routes(client, auth_header):
    """Regular users should get a 403 Forbidden."""
    resp = client.get("/admin/users", headers=auth_header)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden: insufficient role"


def test_unauthenticated_user_cannot_access_admin_routes(client):
    """Unauthenticated requests should get a 401 Unauthorized."""
    resp = client.get("/admin/users")
    assert resp.status_code == 401
