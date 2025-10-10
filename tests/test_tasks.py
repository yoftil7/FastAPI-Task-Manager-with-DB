import pytest


def test_create_task_authenticated(client, auth_header):
    """Ensure an authenticated user can create a task."""
    response = client.post(
        "/tasks",
        json={"title": "test task", "completed": False, "priority": 1},
        headers=auth_header,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "test task"
    assert data["completed"] == False
    assert "id" in data


def test_list_all_tasks_empty(client, auth_header):
    """List all tasks (should be empty initially)."""
    resp = client.get(f"/tasks", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_get_task_by_id(client, auth_header):
    post_resp = client.post(
        f"/tasks",
        json={"title": "new task", "completed": False, "priority": 1},
        headers=auth_header,
    )
    task_id = post_resp.json()["id"]
    resp = client.get(f"/tasks/{task_id}", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id


def test_update_task(client, auth_header):
    post_resp = client.post("/tasks", json={"title": "Initial"}, headers=auth_header)
    task_id = post_resp.json()["id"]
    put_resp = client.put(
        f"/tasks/{task_id}",
        json={"title": "updated", "completed": True},
        headers=auth_header,
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["title"] == "updated"
    assert put_resp.json()["completed"] is True


def test_delete_task(client, auth_header):
    post_resp = client.post(f"/tasks", json={"title": "new task"}, headers=auth_header)
    task_id = post_resp.json()["id"]
    resp = client.delete(f"/tasks/{task_id}", headers=auth_header)
    assert resp.status_code == 204
    get_resp = client.get(f"/tasks/{task_id}", headers=auth_header)
    assert get_resp.status_code == 404
    assert get_resp.json()["detail"] == "Task not found"
