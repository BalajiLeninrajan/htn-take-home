import pytest
import json
from app import app, db, UserModel


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    client = app.test_client()

    with app.app_context():
        db.create_all()
        test_user = UserModel(name="Test User", email="test@example.com", phone="123-456-7890", badge_code="TEST123")  # type: ignore
        db.session.add(test_user)
        db.session.commit()

    yield client

    with app.app_context():
        db.drop_all()


class TestUsersResource:
    def test_user_list(self, client):
        response = client.get("/users")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["name"] == "Test User"


class TestUserResource:
    def test_get_valid_user(self, client):
        response = client.get("/users/1")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"

    def test_get_invalid_user(self, client):
        response = client.get("/users/999")
        assert response.status_code == 404

    def test_update_user(self, client):
        update_data = {"name": "Updated Name", "email": "updated@example.com"}
        response = client.put(
            "/users/1", data=json.dumps(update_data), content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.com"

    def test_update_invalid_user(self, client):
        response = client.put("/users/999")
        assert response.status_code == 404

    def test_partial_update(self, client):
        update_data = {"name": "Partial Update"}
        response = client.put(
            "/users/1", data=json.dumps(update_data), content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Partial Update"
        assert data["email"] == "test@example.com"
