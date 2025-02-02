from extensions import db, app
from models import UserModel, ActivityModel, ScanModel


def create_db():
    with app.app_context():
        db.create_all()


def insert_user(name: str, email: str, phone: str, badge_code: str | None = None):
    with app.app_context():
        user = UserModel(name=name, email=email, phone=phone, badge_code=badge_code)  # type: ignore
        db.session.add(user)
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
