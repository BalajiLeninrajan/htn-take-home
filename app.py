from flask_restful import Resource, marshal_with
from flask import request
from sqlalchemy import func
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
                        "scanned_at": scan.scanned_at,
                    }
                )
        return users


class User(Resource):
    def get_scans(self, user):
        scans = ScanModel.query.filter_by(user_id=user.id).all()
        user.scans = []
        for scan in scans:
            activity = ActivityModel.query.get(scan.activity_id)
            user.scans.append(
                {
                    "activity_name": activity.name if activity else "Unknown",
                    "activity_category": activity.category if activity else "Unknown",
                    "scanned_at": scan.scanned_at,
                }
            )

    @marshal_with(UserModel.fields)
    def get(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found"}, 404

        self.get_scans(user)
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
        self.get_scans(user)
        return user


class Scan(Resource):
    @marshal_with(ScanModel.fields)
    def put(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found"}, 404

        user.updated_at = datetime.now()
        db.session.commit()

        data = request.get_json()
        try:
            activity_name, activity_category = (
                data["activity_name"],
                data["activity_category"],
            )
        except KeyError:
            return {"message": "Missing activity_name or activity_category"}, 400

        activity = ActivityModel.query.filter_by(
            name=activity_name, category=activity_category
        ).first()
        if not activity:
            activity = ActivityModel(name=activity_name, category=activity_category)  # type: ignore
            db.session.add(activity)
            db.session.commit()

        scan = ScanModel(user_id=user_id, activity_id=activity.id)  # type: ignore
        db.session.add(scan)
        db.session.commit()

        scan.activity_name = activity.name  # type: ignore
        scan.activity_category = activity.category  # type: ignore
        return scan


class Scans(Resource):
    @marshal_with(ActivityModel.fields)
    def get(self):
        min_frequency = request.args.get("min_frequency", type=int)
        max_frequency = request.args.get("max_frequency", type=int)
        activity_category = request.args.get("activity_category")

        query = (
            db.session.query(
                ActivityModel.name,
                ActivityModel.category,
                func.count(ScanModel.id).label("frequency"),
            )
            .join(ScanModel, ActivityModel.id == ScanModel.activity_id)
            .group_by(ActivityModel.id)
        )

        if min_frequency:
            query = query.having(func.count(ScanModel.id) >= min_frequency)
        if max_frequency:
            query = query.having(func.count(ScanModel.id) <= max_frequency)
        if activity_category:
            query = query.filter(ActivityModel.category == activity_category)

        return [
            {
                "activity_name": name,
                "activity_category": category,
                "scan_count": count,
            }
            for name, category, count in query.all()
        ]


api.add_resource(Users, "/users")
api.add_resource(User, "/users/<int:user_id>")
api.add_resource(Scan, "/scan/<int:user_id>")
api.add_resource(Scans, "/scans")

if __name__ == "__main__":
    app.run(debug=True)
