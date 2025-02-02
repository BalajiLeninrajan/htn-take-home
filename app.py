from flask_restful import Resource, marshal_with
from flask import request
from sqlalchemy import func
from models import UserModel, ActivityModel, ScanModel
from extensions import api, app, db
from datetime import datetime


class Users(Resource):
    """Resource for handling operations on multiple users."""

    @marshal_with(UserModel.fields)
    def get(self):
        """Retrieve all users with their scan history.

        Returns:
            list: List of all users with their associated scans.
        """
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
    """Resource for handling operations on a single user."""

    def get_scans(self, user):
        """Helper method to fetch and format scan history for a user.

        Args:
            user (UserModel): User object to fetch scans for.
        """
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
        """Retrieve a specific user by ID with their scan history.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            dict: User data with scan history if found, 404 error otherwise.
        """
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return {"message": "User not found"}, 404

        self.get_scans(user)
        return user

    @marshal_with(UserModel.fields)
    def put(self, user_id):
        """Update a specific user's information.

        Args:
            user_id (int): The ID of the user to update.

        Returns:
            dict: Updated user data if found, 404 error otherwise.

        Request body can contain any combination of the following:
            - name (str): User's name
            - email (str): User's email
            - phone (str): User's phone number
            - badge_code (str): User's badge code
        """
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
    """Resource for handling individual scan operations."""

    @marshal_with(ScanModel.fields)
    def put(self, user_id):
        """Create a new scan entry for a user.

        Args:
            user_id (int): The ID of the user creating the scan.

        Returns:
            dict: Created scan data if successful, error message otherwise.

        Request body must contain:
            - activity_name (str): Name of the activity
            - activity_category (str): Category of the activity
        """
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
    """Resource for querying scan statistics."""

    @marshal_with(ActivityModel.fields)
    def get(self):
        """Retrieve scan statistics with optional filtering.

        Query Parameters:
            min_frequency (int, optional): Minimum number of scans
            max_frequency (int, optional): Maximum number of scans
            activity_category (str, optional): Filter by activity category

        Returns:
            list: List of activities with their scan counts matching the criteria.
        """
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
