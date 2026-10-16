"""
Tests for user_status.py
Covers: add_status, modify_status, delete_status, search_status

This module provides unit tests for the status operations in user_status.py, including
adding, modifying, deleting, and searching status records in a social networking
application using an in-memory SQLite database via Peewee DataSet. Tests cover
success cases, failure cases (e.g., duplicates, invalid inputs, database errors),
and edge cases.
"""

import unittest
from unittest.mock import patch
from peewee import IntegrityError
from socialnetwork_model import make_dataset, init_schema
import user_status

# pylint: disable=invalid-name

class UserStatusTests(unittest.TestCase):
    """Test suite for status operations in user_status.py."""

    def setUp(self):
        """Set up a fresh in-memory database and status functions before each test.

        Initializes an in-memory SQLite database, creates the schema, sets up the
        status operation functions (add_status, modify_status, delete_status,
        search_status) from user_status.make_status_ops, and adds a dummy user for
        valid foreign key references in status tests.
        """
        self.ds = make_dataset("sqlite:///:memory:")
        init_schema(self.ds)
        self.status_functions = user_status.make_status_ops(self.ds)
        self.add_status = self.status_functions["add_status"]
        self.modify_status = self.status_functions["modify_status"]
        self.delete_status = self.status_functions["delete_status"]
        self.search_status = self.status_functions["search_status"]

        # Add a dummy user so statuses have a valid FK
        Users, _ = self.ds["Users"], self.ds["Status"]
        Users.insert(user_id="user001", user_name="Test",
                     user_last_name="User", email="test@test.com")

    # ---- add_status ----
    def test_add_status_success(self):
        """Test adding a new status successfully.

        Verifies that add_status returns True and the status can be found via search_status.
        """
        result = self.add_status("s1", "user001", "Hello")
        self.assertTrue(result)
        row = self.search_status("s1")
        self.assertIsNotNone(row)

    def test_add_status_duplicate(self):
        """Test adding a status with a duplicate status_id.

        Verifies that add_status returns False when the status_id already exists.
        """
        self.add_status("s1", "user001", "Hello")
        result = self.add_status("s1", "user001", "Duplicate")
        self.assertFalse(result)

    def test_add_status_invalid_length(self):
        """Test adding a status with a status_text exceeding maximum length.

        Verifies that add_status returns False for a status_text longer than allowed.
        """
        long_text = "x" * 151
        result = self.add_status("s2", "user001", long_text)
        self.assertFalse(result)

    def test_add_status_integrity_error(self):
        """Test adding a status when an IntegrityError occurs.

        Mocks a database IntegrityError and verifies that add_status returns False.
        """
        with patch.object(type(self.ds["Status"]), "insert", side_effect=IntegrityError("fail")):
            result = self.add_status("s3", "user001", "Hi")
            self.assertFalse(result)

    def test_add_status_general_exception(self):
        """Test adding a status when a general exception occurs.

        Mocks a generic database exception and verifies that add_status returns False.
        """
        with patch.object(type(self.ds["Status"]), "insert", side_effect=Exception("boom")):
            result = self.add_status("s4", "user001", "Hi")
            self.assertFalse(result)

    # ---- modify_status ----
    def test_modify_status_success(self):
        """Test modifying an existing status's text successfully.

        Adds a status, modifies its text, and verifies that modify_status returns
        True and the updated status_text is correct.
        """
        self.add_status("s1", "user001", "Hello")
        result = self.modify_status("s1", "Updated")
        self.assertTrue(result)
        row = self.search_status("s1")
        self.assertEqual(row["status_text"], "Updated")

    def test_modify_status_nonexistent(self):
        """Test modifying a non-existent status.

        Verifies that modify_status returns False for a status_id that doesn't exist.
        """
        result = self.modify_status("nope", "Updated")
        self.assertFalse(result)

    def test_modify_status_invalid_length(self):
        """Test modifying a status with a status_text exceeding maximum length.

        Adds a status and attempts to modify with an overly long status_text,
        verifying that modify_status returns False.
        """
        self.add_status("s1", "user001", "Hello")
        long_text = "x" * 151
        result = self.modify_status("s1", long_text)
        self.assertFalse(result)

    def test_modify_status_database_error(self):
        """Test modifying a status when a database error occurs.

        Adds a status, mocks a database exception during update, and verifies that
        modify_status returns False.
        """
        self.add_status("s1", "user001", "Hello")
        with patch.object(type(self.ds["Status"]), "update", side_effect=Exception("fail")):
            result = self.modify_status("s1", "Oops")
            self.assertFalse(result)

    # ---- delete_status ----
    def test_delete_status_success(self):
        """Test deleting an existing status successfully.

        Adds a status, deletes it, and verifies that delete_status returns True and
        the status is no longer found via search_status.
        """
        self.add_status("s1", "user001", "Hello")
        result = self.delete_status("s1")
        self.assertTrue(result)
        row = self.search_status("s1")
        self.assertIsNone(row)

    def test_delete_status_nonexistent(self):
        """Test deleting a non-existent status.

        Verifies that delete_status returns False for a status_id that doesn't exist.
        """
        result = self.delete_status("nope")
        self.assertFalse(result)

    def test_delete_status_database_error(self):
        """Test deleting a status when a database error occurs.

        Adds a status, mocks a database exception during deletion, and verifies that
        delete_status returns False.
        """
        self.add_status("s1", "user001", "Hello")
        with patch.object(type(self.ds["Status"]), "delete", side_effect=Exception("fail")):
            result = self.delete_status("s1")
            self.assertFalse(result)

    # ---- search_status ----
    def test_search_status_found(self):
        """Test searching for an existing status.

        Adds a status and verifies that search_status returns a non-None row with
        the correct status_id.
        """
        self.add_status("s1", "user001", "Hello")
        row = self.search_status("s1")
        self.assertIsNotNone(row)
        self.assertEqual(row["status_id"], "s1")

    def test_search_status_not_found(self):
        """Test searching for a non-existent status.

        Verifies that search_status returns None for a status_id that doesn't exist.
        """
        row = self.search_status("nope")
        self.assertIsNone(row)


if __name__ == "__main__":
    unittest.main()
