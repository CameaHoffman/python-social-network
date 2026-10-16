"""
Tests for users.py
Covers: add_user, modify_user, delete_user, search_user

This module provides unit tests for the user operations in users.py, including
adding, modifying, deleting, and searching users in a social networking application
using an in-memory SQLite database via Peewee DataSet. Tests cover success cases,
failure cases (e.g., duplicates, invalid inputs, database errors), and edge cases.
"""

import unittest
from unittest.mock import patch
import pytest
from peewee import IntegrityError
import socialnetwork_model
from socialnetwork_model import make_dataset, init_schema, get_tables
import users
from users import make_user_ops
from db_manager import DatabaseManager

TEST_DB = "sqlite:///test_social_network.db"
TEST_USER = "testuser"

@pytest.fixture
def ds():
    """Provide a fresh in-memory Peewee DataSet instance for testing.

    This fixture is used by standalone pytest-style tests to avoid reusing
    the same SQLite database between test cases.
    """
    return make_dataset("sqlite:///:memory:")

# pylint: disable=broad-exception-caught
# pylint: disable=protected-access
# pylint: disable=bad-indentation
# pylint: disable=redefined-outer-name

class UserTests(unittest.TestCase):
    """Test suite for user operations in users.py.

    Uses unittest to verify add_user, modify_user, delete_user,
    and search_user functions under various scenarios.
    """

    def setUp(self):
        """Set up a fresh in-memory database and user functions before each test.

        Initializes an in-memory SQLite database, creates the schema, and sets up
        the user operation functions (add_user, modify_user, delete_user, search_user)
        from users.make_user_ops.
        """
        self.ds = make_dataset("sqlite:///:memory:")
        init_schema(self.ds)
        self.user_functions = users.make_user_ops(self.ds)
        self.add_user = self.user_functions["add_user"]
        self.modify_user = self.user_functions["modify_user"]
        self.delete_user = self.user_functions["delete_user"]
        self.search_user = self.user_functions["search_user"]

    # ---- add_user ----
    def test_add_user_success(self):
        """Test adding a new user successfully.

        Verifies that add_user returns True and the user can be found via search_user.
        """
        result = self.add_user("u1", "a@b.com", "Alice", "Smith")
        self.assertTrue(result)
        row = self.search_user("u1")
        self.assertIsNotNone(row)

    def test_add_user_duplicate(self):
        """Test adding a user with a duplicate user_id.

        Verifies that adding a user with an existing user_id returns False.
        """
        self.add_user("u1", "a@b.com", "Alice", "Smith")
        result = self.add_user("u1", "dup@b.com", "Alice2", "Smithy")
        self.assertFalse(result)

    def test_add_user_empty_fields(self):
        """Test adding a user with an empty user_id.

        Verifies that add_user returns False when user_id is empty.
        """
        result = self.add_user("", "a@b.com", "Alice", "Smith")
        self.assertFalse(result)

    def test_add_user_invalid_lengths(self):
        """Test adding a user with a user_id exceeding maximum length.

        Verifies that add_user returns False for a user_id longer than allowed.
        """
        long_id = "u" * 31
        result = self.add_user(long_id, "a@b.com", "Alice", "Smith")
        self.assertFalse(result)

    def test_add_user_integrity_error(self):
        """Test adding a user when an IntegrityError occurs.

        Mocks a database IntegrityError and verifies that add_user returns False.
        """
        with patch.object(type(self.ds["Users"]), "insert", side_effect=IntegrityError("fail")):
            result = self.add_user("u1", "a@b.com", "Alice", "Smith")
            self.assertFalse(result)

    def test_add_user_general_exception(self):
        """Test adding a user when a general exception occurs.

        Mocks a generic database exception and verifies that add_user returns False.
        """
        with patch.object(type(self.ds["Users"]), "insert", side_effect=Exception("boom")):
            result = self.add_user("u1", "a@b.com", "Alice", "Smith")
            self.assertFalse(result)

    # ---- modify_user ----
    def test_modify_user_success(self):
        """Test modifying an existing user's details successfully.

        Adds a user, modifies their email, name, and last name, and verifies that
        modify_user returns True and the updated email is correct.
        """
        self.add_user("u1", "a@b.com", "Alice", "Smith")
        result = self.modify_user("u1", "new@b.com", "Alicia", "Smithy")
        self.assertTrue(result)
        row = self.search_user("u1")
        self.assertEqual(row["email"], "new@b.com")

    def test_modify_user_nonexistent(self):
        """Test modifying a non-existent user.

        Verifies that modify_user returns False for a user_id that doesn't exist.
        """
        result = self.modify_user("nope", "a@b.com", "Alice", "Smith")
        self.assertFalse(result)

    def test_modify_user_invalid_length(self):
        """Test modifying a user with a name exceeding maximum length.

        Adds a user and attempts to modify with an overly long name, verifying that
        modify_user returns False.
        """
        self.add_user("u1", "a@b.com", "Alice", "Smith")
        bad_name = "x" * 31
        result = self.modify_user("u1", "a@b.com", bad_name, "Smith")
        self.assertFalse(result)

    def test_modify_user_database_error(self):
        """Test modifying a user when a database error occurs.

        Adds a user, mocks a database exception during SQL update,
        and verifies that modify_user returns False.
        """
        self.add_user("u1", "a@b.com", "Alice", "Smith")
        with patch.object(self.ds._database, "execute_sql", side_effect=Exception("fail")):
            result = self.modify_user("u1", "new@b.com", "Alice", "Smith")
            self.assertFalse(result)

    # ---- delete_user ----
    def test_delete_user_success(self):
        """Test deleting an existing user successfully.

        Adds a user, deletes them, and verifies that delete_user returns True and
        the user is no longer found via search_user.
        """
        self.add_user("u1", "a@b.com", "Alice", "Smith")
        result = self.delete_user("u1")
        self.assertTrue(result)
        row = self.search_user("u1")
        self.assertIsNone(row)

    def test_delete_user_nonexistent(self):
        """Test deleting a non-existent user.

        Verifies that delete_user returns False for a user_id that doesn't exist.
        """
        result = self.delete_user("nope")
        self.assertFalse(result)

    def test_delete_user_database_error(self):
        """Test deleting a user when a database error occurs.

        Adds a user, mocks a database exception during deletion, and verifies that
        delete_user returns False.
        """
        self.add_user("u1", "a@b.com", "Alice", "Smith")
        with patch.object(type(self.ds["Users"]), "delete", side_effect=Exception("fail")):
            result = self.delete_user("u1")
            self.assertFalse(result)

    # ---- search_user ----
    def test_search_user_found(self):
        """Test searching for an existing user.

        Adds a user and verifies that search_user returns a non-None row with the
        correct user_id.
        """
        self.add_user("u1", "a@b.com", "Alice", "Smith")
        row = self.search_user("u1")
        self.assertIsNotNone(row)
        self.assertEqual(row["user_id"], "u1")

    def test_search_user_not_found(self):
        """Test searching for a non-existent user.

        Verifies that search_user returns None for a user_id that doesn't exist.
        """
        row = self.search_user("nope")
        self.assertIsNone(row)

def test_validate_raises_on_empty_fields():
    """Unit test for _validate helper.

    Ensures that _validate raises ValueError when provided with an empty
    user_id field.
    """
    with pytest.raises(ValueError):
        users._validate("", "a@a.com", "Alice", "Smith")

def test_modify_user_returns_false_if_user_not_found():
    """Unit test for modify_user with missing user.

    Ensures that modify_user returns False when attempting to modify
    a user_id that does not exist in the database.
    """
    with DatabaseManager(TEST_DB) as db:
        socialnetwork_model.create_tables(db)
        ops = users.make_user_ops(db)
        result = ops["modify_user"]("ghost", email="new@example.com")
        assert result is False

def test_delete_user_returns_false_if_user_not_found():
    """Unit test for delete_user with missing user.

    Ensures that delete_user returns False when attempting to delete
    a user_id that does not exist in the database.
    """
    with DatabaseManager(TEST_DB) as db:
        socialnetwork_model.create_tables(db)
        ops = users.make_user_ops(db)
        result = ops["delete_user"]("ghost")
        assert result is False

def test_search_user_returns_none_if_not_found():
    """Unit test for search_user with missing user.

    Ensures that search_user returns None when searching for a user_id
    that does not exist in the database.
    """
    with DatabaseManager(TEST_DB) as db:
        socialnetwork_model.create_tables(db)
        ops = users.make_user_ops(db)
        result = ops["search_user"]("ghost")
        assert result is None

def test_modify_user_updates_only_one(ds):
    """Unit test to confirm modify_user only updates the target row.

    Adds two users, modifies one of them, and verifies that:
    - The modified user's email is updated.
    - The other user's email remains unchanged.
    """
    Users, _, _ = get_tables(ds) #pylint: disable=invalid-name
    ops = make_user_ops(ds)
    modify_user = ops["modify_user"]

    Users.insert(user_id="u1", email="a@a.com", user_name="Alice", user_last_name="Smith")
    Users.insert(user_id="u2", email="b@b.com", user_name="Bob", user_last_name="Brown")

    modify_user("u1", email="new@a.com")

    u1 = Users.find_one(user_id="u1")
    u2 = Users.find_one(user_id="u2")

    assert u1["email"] == "new@a.com"
    assert u2["email"] == "b@b.com"

if __name__ == "__main__":
    unittest.main()
