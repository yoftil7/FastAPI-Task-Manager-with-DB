import pytest


def test_create_task(client, create_user):
    """Test the POST /tasks endpoint."""
    user = create_user()
    response = client.post(
        f"/tasks?user_id={user["id"]}",
        json={"title": "new task", "completed": False, "priority": 1},
    )
    assert response.status_code == 201
    data = response.json()
    assert data == {
        "id": data["id"],
        "title": "new task",
        "completed": False,
        "priority": 1,
        "owner_id": data["id"],
    }


def test_list_all_tasks_without_data(client, create_user):
    user = create_user()
    resp = client.get(f"/tasks?user_id={user["id"]}")
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


def test_list_all_with_data(client, create_user):
    user = create_user()
    client.post(
        f"/tasks?user_id={user["id"]}",
        json={"title": "new task", "completed": False, "priority": 1},
    )
    resp = client.get(f"/tasks?user_id={user['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "new task"
    assert "id" in resp.json()[0]


def test_get_task_with_id(client, create_user):
    user = create_user()
    post_resp = client.post(f"/tasks?user_id={user['id']}", json={"title": "new task"})
    task_id = post_resp.json()["id"]
    resp = client.get(f"/tasks/{task_id}?user_id={user["id"]}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "new task"
    assert resp.json()["id"] == task_id


def test_get_task_with_invalid_id(client, create_user):
    user = create_user()
    get_resp = client.get(f"/tasks/{774}?user_id={user['id']}")
    assert get_resp.status_code == 404
    assert get_resp.json()["detail"] == "Task not found"


def test_update_task(client, create_user):
    user = create_user()
    post_resp = client.post(f"/tasks?user_id={user['id']}", json={"title": "new task"})
    task_id = post_resp.json()["id"]
    resp = client.put(
        f"/tasks/{task_id}?user_id={user["id"]}",
        json={"title": "old task", "completed": True},
    )
    assert resp.json()["title"] == "old task"
    assert resp.json()["completed"] is True
    assert resp.json()["id"] == task_id


def test_delete_task(client, create_user):
    user = create_user()
    post_resp = client.post(f"/tasks?user_id={user["id"]}", json={"title": "new task"})
    task_id = post_resp.json()["id"]
    resp = client.delete(f"/tasks/{task_id}?user_id={user["id"]}")
    assert resp.status_code == 204
    get_resp = client.get(f"/tasks/{task_id}?user_id={user["id"]}")
    assert get_resp.status_code == 404
    assert get_resp.json()["detail"] == "Task not found"


def test_delete_non_existent_task(client, create_user):
    user = create_user()
    del_resp = client.delete(f"/tasks/1?user_id={user["id"]}")
    assert del_resp.status_code == 404
    assert del_resp.json()["detail"] == "Task not found"
