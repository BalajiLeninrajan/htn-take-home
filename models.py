from extensions import db
from flask_restful import fields
from datetime import datetime


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    badge_code = db.Column(db.String(50), unique=True, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    fields = {
        "name": fields.String,
        "email": fields.String,
        "phone": fields.String,
        "badge_code": fields.String,
        "updated_at": fields.DateTime(dt_format="iso8601"),
        "scans": fields.List(
            fields.Nested(
                {
                    "activity_name": fields.String,
                    "scanned_at": fields.DateTime(dt_format="iso8601"),
                    "activity_category": fields.String,
                }
            )
        ),
    }

    def __repr__(self):
        return f"User({self.name}, {self.email})"


class ActivityModel(db.Model):
    __tablename__ = "activity"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=False)

    fields = {
        "name": fields.String,
        "category": fields.String,
    }

    def __repr__(self):
        return f"Activity({self.name}, {self.category})"


class ScanModel(db.Model):
    __tablename__ = "scan"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"), nullable=False)
    scanned_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    fields = {
        "user_id": fields.Integer,
        "activity_name": fields.String,
        "scanned_at": fields.DateTime(dt_format="iso8601"),
        "activity_category": fields.String,
    }

    def __repr__(self):
        return f"Scan({self.user_id}, {self.activity_id}, {self.scanned_at})"
