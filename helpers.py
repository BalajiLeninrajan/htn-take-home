from extensions import db, app
from models import UserModel, ActivityModel, ScanModel
from datetime import datetime


def create_db():
    with app.app_context():
        db.create_all()


def insert_user(name: str, email: str, phone: str, badge_code: str | None = None):
    with app.app_context():
        user = UserModel(name=name, email=email, phone=phone, badge_code=badge_code)  # type: ignore
        db.session.add(user)
        db.session.commit()


def insert_activity(name: str, category: str):
    with app.app_context():
        activity = ActivityModel(name=name, category=category)  # type: ignore
        db.session.add(activity)
        db.session.commit()


def insert_scan(user_id: int, activity_id: int, scanned_at: datetime):
    with app.app_context():
        scan = ScanModel(user_id=user_id, activity_id=activity_id, scanned_at=scanned_at)  # type: ignore
        db.session.add(scan)
        db.session.commit()


def populate_db():
    # TODO: Populate with JSON data
    pass


if __name__ == "__main__":
    create_db()
    insert_user(
        "John Doe",
        "john.doe@example.com",
        "1234567890",
        "give-seven-food-trade",
    )
    insert_activity("opening_ceremony", "activity")
    insert_scan(1, 1, datetime.now())
