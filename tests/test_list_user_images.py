"""Regression tests for the image scanner and database comparison."""

from unittest.mock import Mock

import pytest

from list_user_images import list_user_images, reconcile_images


def test_scan_includes_nested_images_and_their_locations(tmp_path):
    user_folder = tmp_path / "camea"
    nested_folder = user_folder / "family" / "vacation"
    nested_folder.mkdir(parents=True)
    (user_folder / "first.png").touch()
    (nested_folder / "second.PNG").touch()
    (nested_folder / "notes.txt").touch()
    other_user = tmp_path / "other"
    other_user.mkdir()
    (other_user / "private.png").touch()

    assert set(list_user_images("camea", tmp_path)) == {
        ("camea", str(user_folder), "first.png"),
        ("camea", str(nested_folder), "second.PNG"),
    }


def test_scan_missing_user_folder(tmp_path):
    assert list_user_images("missing", tmp_path) == []


def test_scan_skips_directory_symlink_loops(tmp_path):
    user_folder = tmp_path / "camea"
    user_folder.mkdir()
    (user_folder / "photo.png").touch()
    (user_folder / "loop").symlink_to(user_folder, target_is_directory=True)

    assert list_user_images("camea", tmp_path) == [
        ("camea", str(user_folder), "photo.png")
    ]


@pytest.mark.parametrize("path_mode", ["default", "none", "explicit"])
def test_reconcile_matches_nested_files_and_reports_both_differences(
    tmp_path, monkeypatch, path_mode
):
    monkeypatch.chdir(tmp_path)
    image_root = tmp_path / "images"
    folder = image_root / "camea" / "family" / "vacation"
    folder.mkdir(parents=True)
    (folder / "matched.png").touch()
    (folder / "disk_only.png").touch()
    pictures = Mock()
    pictures.find.return_value = [
        {"picture_id": "matched"}, {"picture_id": "db_only"}
    ]
    db = {"Picture": pictures}
    kwargs = {}
    if path_mode == "none":
        kwargs["base_path"] = None
    elif path_mode == "explicit":
        kwargs["base_path"] = image_root

    assert reconcile_images("camea", db, **kwargs) == (
        {"db_only.png"}, {"disk_only.png"}
    )
    pictures.find.assert_called_once_with(user_id="camea")


def test_reconcile_missing_folder_reports_database_images(tmp_path):
    pictures = Mock()
    pictures.find.return_value = [{"picture_id": "missing"}]

    assert reconcile_images("camea", {"Picture": pictures}, tmp_path) == (
        {"missing.png"}, set()
    )


def test_reconcile_empty_database_and_missing_folder(tmp_path):
    pictures = Mock()
    pictures.find.return_value = []

    assert reconcile_images("camea", {"Picture": pictures}, tmp_path) == (
        set(), set()
    )
