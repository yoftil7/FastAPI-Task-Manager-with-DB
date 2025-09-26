import pytest


def test_create_task(client):
    """Test the POST /tasks endpoint."""
    response = client.post(
        "/tasks", json={"title": "new task", "completed": False, "priority": 1}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "new task"
    assert "id" in data
