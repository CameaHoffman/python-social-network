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
    Return (user_id, folder_path, filename) tuples, including nested PNGs.
    Return an empty list if the user's folder doesn't exist.
    """
    folder = Path(base_path) / user_id
    if not folder.exists():
        return []

    def scan_directory(directory):
        images = []
        for item in sorted(directory.iterdir()):
            # Avoid following links that could create directory loops.
            if item.is_symlink():
                continue
            if item.is_dir():
                images.extend(scan_directory(item))
            elif item.is_file() and item.suffix.lower() == ".png":
                images.append((user_id, str(item.parent), item.name))
        return images

    return scan_directory(folder)

def reconcile_images(user_id, db, base_path="images"):
    """
    Compare DB picture records with on-disk `.png` files for one user.
    Returns (missing_on_disk, missing_in_db) as sets of filenames.
    base_path is the image root; the scanner adds the user folder once.
    """
    if base_path is None:
        base_path = "images"

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
