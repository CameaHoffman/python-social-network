"""
Name: Camea Hoffman
Assignment: a09
Description: REST API for the functional social network project.
Provides endpoints for:
- /users       → list all users and their statuses
- /images      → list all users and their images
- /differences → compare DB vs disk images for each user
"""

from pathlib import Path
from flask import Flask
from flask_restful import Api, Resource
from socialnetwork_model import make_dataset, get_tables
import list_user_images

# Initialize dataset and tables
ds = make_dataset()
users_table, status_table, picture_table = get_tables(ds)

app = Flask(__name__)
api = Api(app)


class UsersAPI(Resource):
    """API resource to retrieve all users with their statuses."""

    def get(self):
        """Return a JSON list of users and their associated statuses."""
        result = []
        for user in users_table.all():
            statuses = status_table.find(user_id=user["user_id"])
            result.append({
                "user_id": user["user_id"],
                "email": user["email"],
                "user_name": user["user_name"],
                "user_last_name": user["user_last_name"],
                "statuses": [
                    {"status_id": s["status_id"], "status_text": s["status_text"]}
                    for s in statuses
                ]
            })
        return {"users": result}


class ImagesAPI(Resource):
    """API resource to retrieve all users with their images."""

    def get(self):
        """Return a JSON list of users and their associated images."""
        result = []
        for user in users_table.all():
            pictures = picture_table.find(user_id=user["user_id"])
            result.append({
                "user_id": user["user_id"],
                "email": user["email"],
                "user_name": user["user_name"],
                "user_last_name": user["user_last_name"],
                "pictures": [
                    {"picture_id": p["picture_id"], "tags": p["tags"]}
                    for p in pictures
                ]
            })
        return {"images": result}


class DifferencesAPI(Resource):
    """API resource to compare DB images with files on disk."""

    def get(self):
        """
        Return a JSON list of users with mismatched images.
        Includes:
        - missing_on_disk → in DB but not on disk
        - missing_in_db   → on disk but not in DB
        """
        differences = []
        for user in users_table.all():
            user_id = user["user_id"]
            missing_on_disk, missing_in_db = list_user_images.reconcile_images(
                user_id, ds, base_path=Path("images")
            )

            if missing_on_disk or missing_in_db:
                differences.append({
                    "user_id": user_id,
                    "missing_on_disk": list(missing_on_disk),
                    "missing_in_db": list(missing_in_db)
                })
        return {"differences": differences}


# Register resources to routes
api.add_resource(UsersAPI, "/users")
api.add_resource(ImagesAPI, "/images")
api.add_resource(DifferencesAPI, "/differences")

if __name__ == "__main__":
    app.run(debug=True)
