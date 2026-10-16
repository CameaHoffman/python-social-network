"""
Name: Camea Hoffman
Assignment: a09
Description: Main driver for the functional social network project
"""

import csv
import logging
from pathlib import Path
from peewee import IntegrityError
from socialnetwork_model import make_dataset, create_tables, get_tables
from users import make_user_ops
from user_status import make_status_ops
from db_manager import DatabaseManager
from logger_decorator import log_decorator

DB_URL = "sqlite:///social_network.db"

# pylint: disable=missing-function-docstring
# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-locals
# pylint: disable=invalid-name

logger = logging.getLogger(__name__)


# --- Initialization ---
def init_user_functions(ds=None):
    """Return user operations closure bound to DataSet."""
    ds = ds or make_dataset()
    create_tables(ds)
    return make_user_ops(ds)


def init_status_functions(ds=None):
    """Return status operations closure bound to DataSet."""
    ds = ds or make_dataset()
    create_tables(ds)
    return make_status_ops(ds)


# --- CSV loaders ---
def load_users(filename, user_funcs):
    success = False
    try:
        with open(filename, "r", encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # skip header
            for row_num, row in enumerate(reader, start=2):
                if len(row) < 4 or not all(row):
                    logger.warning("Skipping malformed row %s: %s", row_num, row)
                    continue
                user_id, first, last, email = row
                if user_funcs["add_user"](user_id, email, first, last):
                    success = True
                else:
                    logger.info("Failed to add user %s at row %s", user_id, row_num)
        return success
    except FileNotFoundError:
        logger.error("File not found: %s", filename)
        return False
    except Exception as e:
        logger.error("Error loading users: %s", e)
        return False


def load_status_updates(filename, status_funcs):
    success = False
    try:
        with open(filename, "r", encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # skip header
            for row_num, row in enumerate(reader, start=2):
                if len(row) != 3 or not all(row):
                    logger.warning("Skipping malformed row %s: %s", row_num, row)
                    continue
                status_id, user_id, text = row
                if status_funcs["add_status"](status_id, user_id, text):
                    success = True
                else:
                    logger.info("Failed to add status %s at row %s", status_id, row_num)
        return success
    except FileNotFoundError:
        logger.error("File not found: %s", filename)
        return False
    except Exception as e:
        logger.error("Error loading statuses: %s", e)
        return False


# --- Picture helpers ---
def _generate_picture_id(pictures):
    """Generate the next picture_id (zero-padded 10 digits)."""
    return f"{len(pictures) + 1:010d}"


@log_decorator
def add_picture(user_id, tags, db_url=DB_URL):
    """Add a picture record and file to the system."""
    tag_list = tags.strip().split()
    if not tag_list:  # Reject empty/whitespace-only
        print("ERROR: Tags cannot be empty.")
        return False

    for t in tag_list:
        if not t.startswith("#") or not t[1:].replace("_", "").isalpha():
            print(f"Invalid tag: {t}")
            return False

    sorted_tags = sorted([t.lstrip("#") for t in tag_list])

    with DatabaseManager(db_url) as db:
        user = db["Users"].find_one(user_id=user_id)
        if not user:
            print(f"ERROR: User {user_id} does not exist.")
            return False

        pictures = db["Picture"]
        picture_id = _generate_picture_id(pictures)

        try:
            pictures.insert(
                picture_id=picture_id,
                user_id=user_id,
                tags=" ".join(tag_list)
            )
        except IntegrityError:
            print(f"ERROR: Duplicate picture_id {picture_id}")
            return False
        except Exception as e:
            print(f"Error inserting picture: {e}")
            return False

        # put all user folders under a shared root
        root = Path("images")
        user_dir = root / user_id
        file_path = user_dir
        for tag in sorted_tags:
            file_path = file_path / tag
        file_path.mkdir(parents=True, exist_ok=True)

        img_file = file_path / f"{picture_id}.png"
        img_file.touch(exist_ok=True)

    return True


@log_decorator
def list_user_images(user_id, db_url="sqlite:///social_network.db", base_path="images"):
    """
    List image filenames for a user based on DB and disk.

    - If the user has DB images but folder is missing → raise FileNotFoundError.
    - If the user has no DB images → return empty set even if folder missing.
    """
    ds = make_dataset(db_url)
    _, _, Picture = get_tables(ds)

    # Images in DB
    db_images = {f"{row['picture_id']}.png" for row in Picture.find(user_id=user_id)}

    folder = Path(base_path) / user_id
    if not folder.exists():
        if db_images:
            raise FileNotFoundError(f"Folder not found for user {user_id}: {folder}")
        return set()

    # Images on disk
    disk_images = {f.name for f in folder.glob("*.png") if f.is_file()}

    # Return union (both DB + disk)
    return db_images | disk_images


@log_decorator
def reconcile_images(user_id, db_url="sqlite:///social_network.db", base_path="images"):
    """
    Compare DB images vs disk images for a given user.

    Returns:
        tuple: (missing_on_disk, missing_in_db)
            - missing_on_disk: set of images in DB but not on disk
            - missing_in_db: set of images on disk but not in DB
    """
    ds = make_dataset(db_url)
    _, _, Picture = get_tables(ds)

    # --- images in DB ---
    db_images = {f"{row['picture_id']}.png" for row in Picture.find(user_id=user_id)}

    # --- check folder ---
    folder = Path(base_path) / user_id
    if not folder.exists():
        # If folder missing, all DB images are missing on disk
        return db_images, set()

    # --- images on disk ---
    disk_images = {f.name for f in folder.glob("*.png") if f.is_file()}

    # --- differences ---
    missing_on_disk = db_images - disk_images
    missing_in_db = disk_images - db_images
    return missing_on_disk, missing_in_db


# --- User wrappers ---
def add_user(user_id, email, user_name, user_last_name, user_funcs):
    return user_funcs["add_user"](user_id, email, user_name, user_last_name)


def update_user(user_id, email, user_name, user_last_name, user_funcs):
    return user_funcs["modify_user"](user_id, email, user_name, user_last_name)


def delete_user(user_id, user_funcs):
    return user_funcs["delete_user"](user_id)


def search_user(user_id, user_funcs):
    return user_funcs["search_user"](user_id)


# --- Status wrappers ---
def add_status(status_id, user_id, status_text, status_funcs):
    return status_funcs["add_status"](status_id, user_id, status_text)


def update_status(status_id, status_text, status_funcs):
    return status_funcs["modify_status"](status_id, status_text)


def delete_status(status_id, status_funcs):
    return status_funcs["delete_status"](status_id)


def search_status(status_id, status_funcs):
    return status_funcs["search_status"](status_id)
