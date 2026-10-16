"""
Name: Camea Hoffman
Description: Functional Status API using closures and currying

This module provides a closure-based API for managing status updates in a social
networking application using Peewee DataSet. It includes functions for adding,
modifying, deleting, and searching status records, with validation and logging.
"""

import logging
from peewee import IntegrityError
from socialnetwork_model import get_tables

# pylint: disable=broad-exception-caught
# pylint: disable=invalid-name

logger = logging.getLogger(__name__)

_MAX_STATUS_ID = 30
_MAX_USER_ID = 30
_MAX_TEXT = 150


def _clean(s: str) -> str:
    """Sanitize input string by stripping whitespace and handling None values."""
    return (s or "").strip()


def _validate(status_id: str, user_id: str, status_text: str) -> None:
    """Validate status fields for non-empty values and maximum length constraints."""
    if not all((_clean(status_id), _clean(user_id), _clean(status_text))):
        raise ValueError("All status fields must be non-empty.")
    if len(status_id) > _MAX_STATUS_ID:
        raise ValueError("status_id exceeds max length")
    if len(user_id) > _MAX_USER_ID:
        raise ValueError("user_id exceeds max length")
    if len(status_text) > _MAX_TEXT:
        raise ValueError("status_text exceeds max length")


def make_status_ops(ds):
    """Create a closure-based API for status operations using a DataSet instance."""
    Users, Status, _ = get_tables(ds)

    def add_status(status_id: str, user_id: str, status_text: str) -> bool:
        """Add a new status to the database."""
        try:
            _validate(status_id, user_id, status_text)
            if not Users.find_one(user_id=user_id):
                logger.warning("User %s does not exist. Cannot add status.", user_id)
                return False
            if Status.find_one(status_id=status_id):
                logger.warning("Status %s already exists.", status_id)
                return False
            try:
                Status.insert(**{
                    "status_id": _clean(status_id),
                    "user_id": _clean(user_id),
                    "status_text": _clean(status_text),
                })
                logger.info("Added status %s for user %s.", status_id, user_id)
                return True
            except (IntegrityError, Exception) as exc:
                logger.error("add_status failed: %s", exc)
                return False
        except ValueError as exc:
            logger.error("Validation failed in add_status: %s", exc)
            return False

    def modify_status(status_id: str, status_text: str) -> bool:
        """Update the text of an existing status."""
        _, Status, _ = get_tables(ds)
        row = Status.find_one(status_id=status_id)
        if not row:
            return False

        try:
            new_text = _clean(status_text)
            _validate(status_id, row["user_id"], new_text)
            with ds.transaction():
                Status.update(
                    status_text=new_text,
                    where={"status_id": status_id}
                )

            expected_fields = {"id", "status_id", "user_id", "status_text"}
            updated_row = Status.find_one(status_id=status_id)
            if updated_row and "where" in updated_row:
                updated_row.pop("where", None)
            updated_row = {k: v for k, v in updated_row.items() if k in expected_fields}

            return updated_row and updated_row["status_text"] == new_text
        except (IntegrityError, ValueError, Exception) as exc:
            logger.error("modify_status failed: %s", exc)
            return False

    def delete_status(status_id: str) -> bool:
        """Delete a status from the database."""
        row = Status.find_one(status_id=status_id)
        if not row:
            logger.warning("Status %s not found. Cannot delete.", status_id)
            return False
        try:
            try:
                Status.delete(id=row["id"])
                logger.info("Deleted status %s.", status_id)
                return True
            except (IntegrityError, Exception) as exc:
                logger.error("delete_status failed: %s", exc)
                return False
        except Exception as exc:
            logger.error("Unexpected error in delete_status: %s", exc)
            return False

    def search_status(status_id: str) -> dict | None:
        """Search for a status by its ID."""
        row = Status.find_one(status_id=status_id)
        if row:
            logger.info("Found status %s.", status_id)
            return row
        logger.warning("Status %s not found.", status_id)
        return None

    return {
        "add_status": add_status,
        "modify_status": modify_status,
        "delete_status": delete_status,
        "search_status": search_status,
    }
