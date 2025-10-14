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


def test_pagination(client, sample_tasks):
    """Should return paginated results based on skip & limit."""
    headers = sample_tasks
    resp = client.get("/tasks?skip=0&limit=2", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 2
    assert isinstance(data[0], dict)


def test_filter_by_priority(client, sample_tasks):
    """Should return tasks matching priority filter."""
    headers = sample_tasks
    resp = client.get("/tasks?priority=1", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert all(task["priority"] == 1 for task in data)
    assert len(data) == 2


def test_sorting_desc_by_priority(client, sample_tasks):
    """Should sort tasks by priority descending."""
    headers = sample_tasks
    resp = client.get("/tasks?sort_by=priority&order=desc", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    priorities = [t["priority"] for t in data]
    assert priorities == sorted(priorities, reverse=True)


def test_sorting_invalid_field(client, sample_tasks):
    """Should return 400 if invalid sort field is given."""
    headers = sample_tasks
    resp = client.get("/tasks?sort_by=invalid", headers=headers)
    assert resp.status_code == 400
    assert "Invalid sort field" in resp.json()["detail"]
