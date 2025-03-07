import pytest
from fastapi.testclient import TestClient

def test_create_post(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post(
        "/api/posts/",
        headers=headers,
        json={
            "title": "Test Post",
            "content": "This is a test post"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post"
    assert "id" in data

def test_read_posts(client):
    response = client.get("/api/posts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_post(client, test_user_token):
    # First create a post
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_response = client.post(
        "/api/posts/",
        headers=headers,
        json={
            "title": "Test Post",
            "content": "This is a test post"
        }
    )
    assert post_response.status_code == 201
    post_id = post_response.json()["id"]

    # Then read it
    response = client.get(f"/api/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post"

def test_update_post(client, test_user_token):
    # First create a post
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_response = client.post(
        "/api/posts/",
        headers=headers,
        json={
            "title": "Original Post",
            "content": "Original content"
        }
    )
    assert post_response.status_code == 201
    post_id = post_response.json()["id"]

    # Then update it
    response = client.put(
        f"/api/posts/{post_id}",
        headers=headers,
        json={
            "title": "Updated Post",
            "content": "Updated content"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Post"
    assert data["content"] == "Updated content"

def test_delete_post(client, test_user_token):
    # First create a post
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_response = client.post(
        "/api/posts/",
        headers=headers,
        json={
            "title": "Post to Delete",
            "content": "Content to delete"
        }
    )
    assert post_response.status_code == 201
    post_id = post_response.json()["id"]

    # Then delete it
    response = client.delete(
        f"/api/posts/{post_id}",
        headers=headers
    )
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/posts/{post_id}")
    assert get_response.status_code == 404

def test_create_post_no_auth(client):
    response = client.post(
        "/api/posts/",
        json={
            "title": "Test Post",
            "content": "This is a test post"
        }
    )
    assert response.status_code == 401

def test_update_post_not_owner(client, test_user_token):
    # Create a post as the first user
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_response = client.post(
        "/api/posts/",
        headers=headers,
        json={
            "title": "Original Post",
            "content": "Original content"
        }
    )
    post_id = post_response.json()["id"]

    # Create a second user
    second_user_response = client.post(
        "/api/auth/register",
        json={
            "email": "second@example.com",
            "username": "seconduser",
            "password": "password123"
        }
    )
    
    # Login as second user
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "second@example.com",
            "password": "password123"
        }
    )
    second_token = login_response.json()["access_token"]

    # Try to update first user's post
    response = client.put(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {second_token}"},
        json={
            "title": "Updated Post",
            "content": "Updated content"
        }
    )
    assert response.status_code == 403

def test_delete_post_not_owner(client, test_user_token):
    # Create a post as the first user
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_response = client.post(
        "/api/posts/",
        headers=headers,
        json={
            "title": "Post to Delete",
            "content": "Content to delete"
        }
    )
    post_id = post_response.json()["id"]

    # Create a second user
    second_user_response = client.post(
        "/api/auth/register",
        json={
            "email": "second@example.com",
            "username": "seconduser",
            "password": "password123"
        }
    )
    
    # Login as second user
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "second@example.com",
            "password": "password123"
        }
    )
    second_token = login_response.json()["access_token"]

    # Try to delete first user's post
    response = client.delete(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 403

def test_get_nonexistent_post(client, test_user_token, monkeypatch):
    response = client.get("/api/posts/99999")
    assert response.status_code == 404