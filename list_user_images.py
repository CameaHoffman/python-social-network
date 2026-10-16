"""
Name: Camea Hoffman
Description: Recursive image listing and reconciliation for social network project.

This module provides:
- list_user_images: Recursively walks through a user’s image directory and
  returns all `.png` files as tuples with (user_id, full_path, filename).
- reconcile_images: Compares the database picture records against the actual
  files on disk for a given user, reporting mismatches.
"""

from pathlib import Path

def list_user_images(user_id, base_path="images"):
    """
    List all image files for a given user on disk.
    Returns an empty set if the folder doesn't exist (instead of raising).
    """
    folder = Path(base_path) / user_id
    if not folder.exists():
        return set()   # instead of raising
    return {f.name for f in folder.glob("*.png") if f.is_file()}

def reconcile_images(user_id, db, base_path=None):
    """
    Compare DB picture records with on-disk `.png` files for one user.
    Returns (missing_on_disk, missing_in_db) as sets of filenames.
    """
    if base_path is None:
        base_path = Path("images") / user_id

    # --- DB side ---
    db_pictures = db["Picture"].find(user_id=user_id)
    db_files = {f"{row['picture_id']}.png" for row in db_pictures}

    # --- Disk side ---
    disk_tuples = list_user_images(user_id, base_path)
    disk_files = {filename for _, _, filename in disk_tuples}

    # --- Compare ---
    missing_on_disk = db_files - disk_files          # in DB, not on disk
    missing_in_db = disk_files - db_files            # on disk, not in DB
    return missing_on_disk, missing_in_db
