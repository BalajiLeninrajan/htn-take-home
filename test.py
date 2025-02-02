from time import sleep
import pytest
import json
from app import app, db, UserModel, ActivityModel, ScanModel


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
        assert data[0]["scans"] == []


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
        initial_response = client.get("/users/1")
        initial_data = json.loads(initial_response.data)
        initial_updated_at = initial_data["updated_at"]

        update_data = {"name": "Updated Name", "email": "updated@example.com"}
        response = client.put(
            "/users/1", data=json.dumps(update_data), content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.com"
        assert data["updated_at"] != initial_updated_at

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


class TestScanResource:
    def test_valid_scan_new_activity(self, client):
        # Test scanning with new activity
        response = client.put(
            "/scan/1",
            data=json.dumps(
                {"activity_name": "giving_go_a_go", "activity_category": "workshop"}
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["activity_name"] == "giving_go_a_go"
        assert data["activity_category"] == "workshop"
        assert "scanned_at" in data

        with app.app_context():
            assert ActivityModel.query.count() == 1
            assert ScanModel.query.count() == 1

    def test_valid_scan_existing_activity(self, client):
        with app.app_context():
            activity = ActivityModel(name="opening_ceremony", category="activity")  # type: ignore
            db.session.add(activity)
            db.session.commit()

        response = client.put(
            "/scan/1",
            data=json.dumps(
                {"activity_name": "opening_ceremony", "activity_category": "activity"}
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["activity_name"] == "opening_ceremony"
        assert data["activity_category"] == "activity"

        with app.app_context():
            assert ActivityModel.query.count() == 1
            assert ScanModel.query.count() == 1

    def test_scan_invalid_user(self, client):
        response = client.put(
            "/scan/999",
            data=json.dumps({"activity_name": "Test", "activity_category": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_scan_missing_fields(self, client):
        # Missing activity_category
        response = client.put(
            "/scan/1",
            data=json.dumps({"activity_name": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 400

        # Missing activity_name
        response = client.put(
            "/scan/1",
            data=json.dumps({"activity_category": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 400
