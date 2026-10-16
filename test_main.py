"""
Name: Camea Hoffman
Description: Integration-level tests for main.py
Covers: load_users, load_status_updates, wrapper functions,
        picture reconciliation, DatabaseManager, and log_decorator
"""

import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import playhouse.dataset
import pytest
import peewee
import main
import socialnetwork_model
from db_manager import DatabaseManager
from logger_decorator import log_decorator #pylint: disable=unused=import

TEST_USER = "testuser"

#pylint: disable=redefined-outer-name
#pylint: disable=unnecessary-dunder-call
#pylint: disable=use-implicit-booleaness-not-comparison


# -------------------------------
# unittest class for CSV loaders
# -------------------------------

class MainTests(unittest.TestCase):
    """Integration tests for CSV loader functions in main.py"""

    def test_load_users_success(self):
        """Test load_users works with valid CSV input."""
        csv_data = "USER_ID,EMAIL,FIRST,LAST\nu1,a@b.com,Alice,Smith\n"
        funcs = {"add_user": lambda *a: True}
        with patch("builtins.open", mock_open(read_data=csv_data)):
            assert main.load_users("fake.csv", funcs)

    def test_load_users_malformed(self):
        """Test load_users skips malformed rows with missing fields."""
        csv_data = "USER_ID,EMAIL,FIRST,LAST\nu1,a@b.com,Alice\n"
        funcs = {"add_user": lambda *a: True}
        with patch("builtins.open", mock_open(read_data=csv_data)):
            assert not main.load_users("fake.csv", funcs)

    def test_load_users_file_not_found(self):
        """Test load_users handles missing CSV file gracefully."""
        funcs = {"add_user": lambda *a: True}
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert not main.load_users("nofile.csv", funcs)

    def test_load_users_general_exception(self):
        """Test load_users handles unexpected errors."""
        funcs = {"add_user": lambda *a: True}
        with patch("builtins.open", side_effect=Exception("boom")):
            assert not main.load_users("nofile.csv", funcs)

    def test_load_status_success(self):
        """Test load_status_updates works with valid CSV input."""
        csv_data = "STATUS_ID,USER_ID,TEXT\ns1,u1,Hello\n"
        funcs = {"add_status": lambda *a: True}
        with patch("builtins.open", mock_open(read_data=csv_data)):
            assert main.load_status_updates("fake.csv", funcs)

    def test_load_status_malformed(self):
        """Test load_status_updates skips malformed rows."""
        csv_data = "STATUS_ID,USER_ID,TEXT\ns1,u1\n"
        funcs = {"add_status": lambda *a: True}
        with patch("builtins.open", mock_open(read_data=csv_data)):
            assert not main.load_status_updates("fake.csv", funcs)

    def test_load_status_file_not_found(self):
        """Test load_status_updates handles missing file."""
        funcs = {"add_status": lambda *a: True}
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert not main.load_status_updates("nofile.csv", funcs)

    def test_load_status_general_exception(self):
        """Test load_status_updates handles unexpected errors."""
        funcs = {"add_status": lambda *a: True}
        with patch("builtins.open", side_effect=Exception("boom")):
            assert not main.load_status_updates("nofile.csv", funcs)


# -------------------------------
# Fixtures
# -------------------------------

@pytest.fixture(autouse=True)
def clean_db(tmp_path):
    """Fixture: creates a temporary SQLite DB file and cleans up after tests."""
    db_file = tmp_path / "test_social_network.db"
    db_url = f"sqlite:///{db_file}"
    yield db_url
    if db_file.exists():
        db_file.unlink()


# -------------------------------
# Wrapper function tests
# -------------------------------

def test_user_wrappers():
    """Test user wrapper functions call closures correctly."""
    funcs = {
        "add_user": lambda *_: "added",
        "modify_user": lambda *_: "modified",
        "delete_user": lambda *_: "deleted",
        "search_user": lambda *_: "found",
    }
    assert main.add_user("u1", "a@b.com", "A", "B", funcs) == "added"
    assert main.update_user("u1", "a@b.com", "A", "B", funcs) == "modified"
    assert main.delete_user("u1", funcs) == "deleted"
    assert main.search_user("u1", funcs) == "found"


def test_user_wrappers_missing_key():
    """Test missing user wrapper key raises KeyError."""
    funcs = {}  # missing add_user
    with pytest.raises(KeyError):
        main.add_user("u1", "a@b.com", "A", "B", funcs)


def test_status_wrappers():
    """Test status wrapper functions call closures correctly."""
    funcs = {
        "add_status": lambda *_: "added",
        "modify_status": lambda *_: "modified",
        "delete_status": lambda *_: "deleted",
        "search_status": lambda *_: "found",
    }
    assert main.add_status("s1", "u1", "hi", funcs) == "added"
    assert main.update_status("s1", "new", funcs) == "modified"
    assert main.delete_status("s1", funcs) == "deleted"
    assert main.search_status("s1", funcs) == "found"


# -------------------------------
# Picture + Reconcile tests
# -------------------------------

def test_add_picture_success(clean_db):
    """Test add_picture works with valid user and tags."""
    with DatabaseManager(clean_db) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id=TEST_USER, email="t@t.com",
                           user_name="Test", user_last_name="User")
    assert main.add_picture(TEST_USER, "#car #sports", db_url=clean_db)


def test_add_picture_invalid_tag(clean_db):
    """Test add_picture rejects invalid tags."""
    with DatabaseManager(clean_db) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id=TEST_USER, email="t@t.com",
                           user_name="Test", user_last_name="User")
    assert not main.add_picture(TEST_USER, "car", db_url=clean_db)


def test_add_picture_empty_tags(clean_db):
    """Test add_picture rejects whitespace-only tags."""
    with DatabaseManager(clean_db) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id="picless", email="p@p.com",
                           user_name="Pic", user_last_name="Less")
    assert not main.add_picture("picless", "   ", db_url=clean_db)


def test_add_picture_integrity_error(monkeypatch, clean_db):
    """Test add_picture handles IntegrityError on insert."""
    with DatabaseManager(clean_db) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id=TEST_USER, email="t@t.com",
                           user_name="Test", user_last_name="User")

    def fake_insert(*a, **k):
        raise peewee.IntegrityError("forced")
    monkeypatch.setattr(playhouse.dataset.Table, "insert", fake_insert)

    assert not main.add_picture(TEST_USER, "#car", db_url=clean_db)


def test_list_user_images_and_missing_user(clean_db):
    """Test list_user_images returns empty set for unknown user with no DB images."""
    with DatabaseManager(clean_db) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id=TEST_USER, email="x@x.com",
                           user_name="X", user_last_name="Y")
    main.add_picture(TEST_USER, "#car", db_url=clean_db)
    assert main.list_user_images(TEST_USER, db_url=clean_db)

    # ghost has no DB images, so should return empty set
    images = main.list_user_images("ghost", db_url=clean_db)
    assert images == set()


def test_list_user_images_with_existing_file(clean_db):
    """Test list_user_images includes pre-existing files in user folder."""
    user = "picuser"
    with DatabaseManager(clean_db) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id=user, email="u@u.com",
                           user_name="U", user_last_name="S")

    user_dir = Path("images") / user
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / "demo.png").write_text("fake")

    images = main.list_user_images(user, db_url=clean_db)
    assert "demo.png" in images


def test_list_user_images_user_folder_missing(clean_db):
    """Test list_user_images raises FileNotFoundError if folder missing but DB has images."""
    with DatabaseManager(clean_db) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id="u123", email="x@x.com",
                           user_name="X", user_last_name="Y")
        db["Picture"].insert(picture_id="p1", user_id="u123", tags="#tag")

    with pytest.raises(FileNotFoundError):
        main.list_user_images("u123", db_url=clean_db)


def test_reconcile_images_mixed(clean_db):
    """Test reconcile_images detects mismatches between DB and disk."""
    user = "mixuser"
    with DatabaseManager(clean_db) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id=user, email="m@m.com",
                           user_name="Mix", user_last_name="User")
        db["Picture"].insert(picture_id="p_in_db", user_id=user, tags="#tag")

    user_dir = Path("images") / user
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / "p_on_disk.png").write_text("fake")

    missing_on_disk, missing_in_db = main.reconcile_images(user, db_url=clean_db)
    assert "p_in_db.png" in missing_on_disk
    assert "p_on_disk.png" in missing_in_db


def test_reconcile_images_missing_folder(clean_db):
    """Test reconcile_images reports DB-only images if folder missing."""
    db_file = Path(clean_db.split("///")[-1])
    db_url = f"sqlite:///{db_file}"
    with DatabaseManager(db_url) as db:
        socialnetwork_model.create_tables(db)
        db["Users"].insert(user_id="u404", email="x@x.com",
                           user_name="X", user_last_name="Y")
        db["Picture"].insert(picture_id="p404", user_id="u404", tags="#tag")
    missing_on_disk, missing_in_db = main.reconcile_images("u404", db_url=db_url)
    assert missing_on_disk == {"p404.png"}
    assert missing_in_db == set()
