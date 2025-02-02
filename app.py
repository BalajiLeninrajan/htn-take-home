from flask_restful import Resource, marshal_with
from flask import request
from models import UserModel, ActivityModel, ScanModel
from extensions import api, app, db
from datetime import datetime


class Users(Resource):
    @marshal_with(UserModel.fields)
    def get(self):
        users = UserModel.query.all()
        for user in users:
            scans = ScanModel.query.filter_by(user_id=user.id).all()
            user.scans = []
            for scan in scans:
                activity = ActivityModel.query.get(scan.activity_id)
                user.scans.append(
                    {
                        "activity_name": activity.name if activity else "Unknown",
                        "activity_category": (
                            activity.category if activity else "Unknown"
                        ),
                        "scanned_at": scan.timestamp,
                    }
                )
        return users


class User(Resource):
    @marshal_with(UserModel.fields)
    def get(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found"}, 404

        scans = ScanModel.query.filter_by(user_id=user_id).all()
        user.scans = []
        for scan in scans:
            activity = ActivityModel.query.get(scan.activity_id)
            user.scans.append(
                {
                    "activity_name": activity.name if activity else "Unknown",
                    "activity_category": activity.category if activity else "Unknown",
                    "scanned_at": scan.timestamp,
                }
            )
        return user

    @marshal_with(UserModel.fields)
    def put(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found"}, 404

        data = request.get_json()

        if "name" in data:
            user.name = data["name"]
        if "email" in data:
            user.email = data["email"]
        if "phone" in data:
            user.phone = data["phone"]
        if "badge_code" in data:
            user.badge_code = data["badge_code"]

        user.updated_at = datetime.now()
        db.session.commit()
        return user


api.add_resource(Users, "/users")
api.add_resource(User, "/users/<int:user_id>")

if __name__ == "__main__":
    app.run(debug=True)
