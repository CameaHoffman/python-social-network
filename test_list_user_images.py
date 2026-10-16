"""Regression tests for the image scanner and database comparison."""

from list_user_images import list_user_images


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
