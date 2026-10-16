"""
Name: Camea Hoffman
Description: Extra coverage tests for DatabaseManager, log_decorator,
             and add_picture validation logic.
"""

import logging
import pytest
from db_manager import DatabaseManager
from logger_decorator import log_decorator
import main
from test_main import clean_db #pylint: disable=unused-import
from socialnetwork_model import create_tables

#pylint: disable=unnecessary-dunder-call
#pylint: disable=redefined-outer-name
#pylint: disable=import-outside-toplevel


def test_db_manager_manual_methods(tmp_path):
    """Test DatabaseManager __enter__ and manual __exit__ calls."""
    db_file = tmp_path / "manual.db"
    db_url = f"sqlite:///{db_file}"
    mgr = DatabaseManager(db_url)
    db = mgr.__enter__()
    assert hasattr(db, "tables")
    # manually trigger __exit__ with exc_type to simulate error cleanup
    mgr.__exit__(RuntimeError, RuntimeError("boom"), None)
    assert db_file.exists()


def test_log_decorator_debug_and_info(caplog):
    """Test log_decorator logs function calls at DEBUG/INFO levels."""
    @log_decorator
    def dummy(x):
        return x * 2

    caplog.set_level(logging.DEBUG)
    result = dummy(5)
    assert result == 10
    assert "dummy" in caplog.text


def test_log_decorator_raises_and_logs(caplog):
    """Test log_decorator logs exceptions when function raises."""
    @log_decorator
    def bad():
        raise ValueError("bad!")

    with pytest.raises(ValueError):
        bad()
    assert "bad" in caplog.text


def test_add_picture_tag_validation(clean_db):
    """Test add_picture rejects invalid or empty tags."""
    with DatabaseManager(clean_db) as db:
        create_tables(db)
        db["Users"].insert(user_id="u1", email="a@b.com", user_name="A", user_last_name="B")

    # bad tag format (missing #)
    assert not main.add_picture("u1", "not_a_tag", db_url=clean_db)

    # empty tags
    assert not main.add_picture("u1", "", db_url=clean_db)
