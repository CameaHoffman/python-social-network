"""
Name: Camea Hoffman
Assignment: a08
Description: Functional Users API using closures and currying
"""

import logging
from peewee import IntegrityError
from socialnetwork_model import get_tables

# pylint: disable=broad-exception-caught
# pylint: disable=invalid-name
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-statements

logger = logging.getLogger(__name__)

# --- Validation helpers ---
_MAX_ID = 30
_MAX_NAME = 30
_MAX_LAST = 100


def _clean(s: str) -> str:
    return (s or "").strip()


def _validate(user_id: str, email: str, user_name: str, user_last_name: str) -> None:
    """
    Raise ValueError if fields are empty or exceed length limits.
    """
    uid = _clean(user_id)
    eml = _clean(email)
    fn = _clean(user_name)
    ln = _clean(user_last_name)

    if not (uid and eml and fn and ln):
        raise ValueError("All user fields must be non-empty.")

    if len(uid) > _MAX_ID:
        raise ValueError("user_id exceeds 30 characters.")
    if len(fn) > _MAX_NAME:
        raise ValueError("user_name exceeds 30 characters.")
    if len(ln) > _MAX_LAST:
        raise ValueError("user_last_name exceeds 100 characters.")


def make_user_ops(ds):
    """
    Return a dict of user operations, closed over a DataSet.
    Example:
        ops = make_user_ops(ds)
        ops["add_user"]("u1", "a@a.com", "Alice", "Smith")
    """

    def add_user(user_id, email, user_name, user_last_name):
        """Add a user. Returns True on success, False on invalid/duplicate/error."""
        try:
            _validate(user_id, email, user_name, user_last_name)

            Users, _, _ = get_tables(ds)

            try:
                if Users.find_one(user_id=_clean(user_id)):
                    logger.warning("User %s already exists.", user_id)
                    return False
            except Exception as exc:  # pragma: no cover (defensive)
                logger.error("find_one failed in add_user: %s", exc)
                return False

            try:
                Users.insert(
                    user_id=_clean(user_id),
                    email=_clean(email),
                    user_name=_clean(user_name),
                    user_last_name=_clean(user_last_name),
                )
                logger.info("Added user %s.", user_id)
                return True
            except (IntegrityError, Exception) as exc:
                logger.error("insert failed in add_user: %s", exc)
                return False

        except (ValueError, IntegrityError, Exception) as exc:
            logger.error("add_user failed: %s", exc)
            return False

    def modify_user(user_id, email=None, user_name=None, user_last_name=None):
        """Modify existing user. Returns True on success, False if not found/invalid/error."""
        try:
            Users, _, _ = get_tables(ds)

            row = Users.find_one(user_id=_clean(user_id))
            if not row:
                return False

            new_email = _clean(email) if email is not None else row.get("email", "")
            new_name = _clean(user_name) if user_name is not None else row.get("user_name", "")
            new_last = _clean(user_last_name) if user_last_name is not None else row.get(
                "user_last_name", "")

            _validate(user_id, new_email, new_name, new_last)

            ds._database.execute_sql( #pylint: disable=protected-access
                "UPDATE Users SET email=?, user_name=?, user_last_name=? WHERE user_id=?",
                (new_email, new_name, new_last, _clean(user_id))
            )

            updated = Users.find_one(user_id=_clean(user_id))
            return (
                updated
                and updated.get("email") == new_email
                and updated.get("user_name") == new_name
                and updated.get("user_last_name") == new_last
            )

        except (ValueError, IntegrityError, Exception) as exc:
            logger.error("modify_user failed: %s", exc)
            return False

    def delete_user(user_id):
        """Delete user (and cascade delete statuses). Returns True on success, False otherwise."""
        try:
            Users, Status, _ = get_tables(ds)  # ✅ unpack 3 values

            try:
                row = Users.find_one(user_id=_clean(user_id))
            except Exception as exc:
                logger.error("find_one failed in delete_user: %s", exc)
                return False

            if not row:
                return False

            try:
                Status.delete(user_id=_clean(user_id))
            except Exception as exc:
                logger.error("status cascade delete failed: %s", exc)
                return False

            try:
                Users.delete(user_id=_clean(user_id))
                return True
            except (IntegrityError, Exception) as exc:
                logger.error("delete failed in delete_user: %s", exc)
                return False

        except (IntegrityError, Exception) as exc:
            logger.error("delete_user failed: %s", exc)
            return False

    def search_user(user_id):
        """Return user row dict if found, else None."""
        try:
            Users, _, _ = get_tables(ds)  # ✅ unpack 3 values
            try:
                row = Users.find_one(user_id=_clean(user_id))
            except Exception as exc:
                logger.error("find_one failed in search_user: %s", exc)
                return None

            if row:
                logger.info("Found user %s.", user_id)
                return row

            logger.warning("User %s not found.", user_id)
            return None

        except Exception as exc:
            logger.error("search_user failed: %s", exc)
            return None

    return {
        "add_user": add_user,
        "modify_user": modify_user,
        "delete_user": delete_user,
        "search_user": search_user,
    }
