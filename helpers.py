import json
from extensions import db, app
from models import UserModel, ActivityModel, ScanModel
from datetime import datetime


def create_db():
    with app.app_context():
        db.create_all()


def insert_user(name: str, email: str, phone: str, badge_code: str | None = None):
    user = UserModel(name=name, email=email, phone=phone, badge_code=badge_code)  # type: ignore
    db.session.add(user)
    db.session.commit()
    return user


def insert_activity(name: str, category: str):
    activity = ActivityModel(name=name, category=category)  # type: ignore
    db.session.add(activity)
    db.session.commit()
    return activity


def insert_scan(user_id: int, activity_id: int, scanned_at: datetime):
    scan = ScanModel(user_id=user_id, activity_id=activity_id, scanned_at=scanned_at)  # type: ignore
    db.session.add(scan)
    db.session.commit()
    return scan


def populate_db():
    # TODO: Populate with JSON data
    with app.app_context():
        with open("data.json", "r") as f:
            data = json.load(f)

        for element in data:
            user = insert_user(
                element["name"],
                element["email"],
                element["phone"],
                element["badge_code"] if element["badge_code"] != "" else None,
            )
            for scan in element["scans"]:
                activity = ActivityModel.query.filter_by(
                    name=scan["activity_name"], category=scan["activity_category"]
                ).first()
                if activity is None:
                    activity = insert_activity(
                        scan["activity_name"], scan["activity_category"]
                    )
                scanned_at = datetime.fromisoformat(scan["scanned_at"])
                insert_scan(user.id, activity.id, scanned_at)


if __name__ == "__main__":
    create_db()
    populate_db()
