"""
Name: Camea Hoffman
Date: February 2025
Assignment 10 (Flask API)

This module implements a Flask REST API for the social network project.
It exposes three endpoints:

- /users        → Returns all users with their profile details and statuses
- /images       → Returns all users with their associated images and tags
- /differences  → Compares database entries vs. disk images and reports mismatches

The API integrates with the Peewee DataSet database (via socialnetwork_model)
and reuses logic from list_user_images to reconcile images.
"""

import pytest
import api
#pylint: disable=redefined-outer-name

@pytest.fixture
def client():
    """Provide a Flask test client for API testing."""
    api.app.config["TESTING"] = True
    with api.app.test_client() as client:
        yield client

def test_users_endpoint(client):
    """Ensure /users endpoint returns JSON with 'users' key."""
    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data

def test_images_endpoint(client):
    """Ensure /images endpoint returns JSON with 'images' key."""
    response = client.get("/images")
    assert response.status_code == 200
    data = response.get_json()
    assert "images" in data

def test_differences_endpoint(client):
    """Ensure /differences endpoint returns JSON with 'differences' key."""
    response = client.get("/differences")
    assert response.status_code == 200
    data = response.get_json()
    assert "differences" in data
