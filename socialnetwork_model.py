"""
Name: Camea Hoffman
Description: Database schema and helpers for social network project
"""

import logging
from playhouse.dataset import DataSet

logger = logging.getLogger(__name__)

DB_URL = "sqlite:///social_network.db"


def make_dataset(db_url: str = DB_URL):
    """Return a Peewee DataSet bound to the given database URL."""
    return DataSet(db_url)


def init_schema(ds):
    """Ensure Users, Status, and Picture tables exist with proper schema."""

    users = ds["Users"]
    status = ds["Status"]
    picture = ds["Picture"]

    # Bootstrap Users
    if not users.find_one():
        users.insert(user_id="__dummy__", email="dummy@example.com",
                     user_name="Dummy", user_last_name="User")
        users.delete(user_id="__dummy__")

    # Bootstrap Status
    if not status.find_one():
        status.insert(status_id="__dummy__", user_id="__dummy__", status_text="Dummy")
        status.delete(status_id="__dummy__")

    # Bootstrap Picture
    if not picture.find_one():
        picture.insert(picture_id="__dummy__", user_id="__dummy__", tags="#dummy")
        picture.delete(picture_id="__dummy__")

    # Add indices
    users.create_index(["user_id"], unique=True)
    status.create_index(["status_id"], unique=True)
    picture.create_index(["picture_id"], unique=True)

    logger.info("Schema initialized: Users, Status, Picture ready.")


def get_tables(ds):
    """Return Users, Status, Picture tables for convenience."""
    return ds["Users"], ds["Status"], ds["Picture"]


def create_tables(ds):
    """Alias for init_schema to avoid breaking old imports/tests."""
    return init_schema(ds)
