"""
Name: Camea Hoffman
Description: Unit tests for menu.py functions

This module provides unit tests for the menu.py module, which serves as the front-end
interface for a social networking application. Tests cover user and status operations
(load_users, load_status_updates, add_user, update_user, search_user, delete_user,
add_status, update_status, search_status, delete_status), the quit_program function,
and the run_menu function, including success, failure, and invalid input scenarios.
"""

import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
import menu

# pylint: disable=unused-argument
# pylint: disable=too-many-public-methods

class MenuTests(TestCase):
    """Test suite for menu.py functions."""

    def setUp(self):
        """Set up mock user and status function dictionaries before each test.

        Creates mock dictionaries for user_funcs and status_funcs to simulate
        main.py operations, and patches the global user_funcs and status_funcs
        in menu.py to use these mocks.
        """
        # Create mock dicts for user_funcs and status_funcs
        self.mock_user_funcs = {
            "add_user": MagicMock(),
            "modify_user": MagicMock(),
            "delete_user": MagicMock(),
            "search_user": MagicMock(),
        }
        self.mock_status_funcs = {
            "add_status": MagicMock(),
            "modify_status": MagicMock(),
            "delete_status": MagicMock(),
            "search_status": MagicMock(),
        }

        # Patch the globals in menu.py
        patcher_user = patch("menu.user_funcs", self.mock_user_funcs)
        patcher_status = patch("menu.status_funcs", self.mock_status_funcs)
        self.addCleanup(patcher_user.stop)
        self.addCleanup(patcher_status.stop)
        patcher_user.start()
        patcher_status.start()

    # -------- USERS --------
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["users.csv"])
    @patch("menu.main.load_users", return_value=True)
    def test_load_users_success(self, mock_load, mock_input, mock_print):
        """Test loading users successfully from a file.

        Verifies that load_users calls main.load_users with the correct filename
        and prints a success message.
        """
        menu.load_users()
        mock_load.assert_called_with("users.csv", self.mock_user_funcs)
        mock_print.assert_called_once_with("User database loaded successfully.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["users.csv"])
    @patch("menu.main.load_users", return_value=False)
    def test_load_users_failure(self, mock_load, mock_input, mock_print):
        """Test loading users when the operation fails.

        Verifies that load_users calls main.load_users and prints a failure message
        when the operation returns False.
        """
        menu.load_users()
        mock_load.assert_called_with("users.csv", self.mock_user_funcs)
        self.assertTrue(any("Failed to load user database." in call[0][0]
                            for call in mock_print.call_args_list))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1", "email", "First", "Last"])
    def test_add_user_success(self, mock_input, mock_print):
        """Test adding a user successfully.

        Verifies that add_user calls the mocked add_user function and prints a
        success message when the operation returns True.
        """
        self.mock_user_funcs["add_user"].return_value = True
        menu.add_user()
        mock_print.assert_called_once_with("User was successfully added.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1", "email", "First", "Last"])
    def test_add_user_failure(self, mock_input, mock_print):
        """Test adding a user when the operation fails.

        Verifies that add_user calls the mocked add_user function and prints an
        error message when the operation returns False.
        """
        self.mock_user_funcs["add_user"].return_value = False
        menu.add_user()
        self.assertTrue(any("An error occurred" in call[0][0]
                            for call in mock_print.call_args_list))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1", "email", "First", "Last"])
    def test_update_user_success(self, mock_input, mock_print):
        """Test updating a user successfully.

        Verifies that update_user calls the mocked modify_user function and prints
        a success message when the operation returns True.
        """
        self.mock_user_funcs["modify_user"].return_value = True
        menu.update_user()
        mock_print.assert_called_once_with("User was successfully updated.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1", "email", "First", "Last"])
    def test_update_user_failure(self, mock_input, mock_print):
        """Test updating a user when the operation fails.

        Verifies that update_user calls the mocked modify_user function and prints
        an error message when the operation returns False.
        """
        self.mock_user_funcs["modify_user"].return_value = False
        menu.update_user()
        self.assertTrue(any("An error occurred" in call[0][0]
                            for call in mock_print.call_args_list))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1"])
    def test_search_user_found(self, mock_input, mock_print):
        """Test searching for an existing user.

        Verifies that search_user calls the mocked search_user function and prints
        the user details when a user is found.
        """
        self.mock_user_funcs["search_user"].return_value = {
            "user_id": "u1", "email": "e", "user_name": "First", "user_last_name": "Last"
        }
        menu.search_user()
        self.assertTrue(any("User ID: u1" in call[0][0]
                            for call in mock_print.call_args_list))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1"])
    def test_search_user_not_found(self, mock_input, mock_print):
        """Test searching for a non-existent user.

        Verifies that search_user calls the mocked search_user function and prints
        an error message when no user is found.
        """
        self.mock_user_funcs["search_user"].return_value = None
        menu.search_user()
        mock_print.assert_called_once_with("ERROR: User does not exist.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1"])
    def test_delete_user_success(self, mock_input, mock_print):
        """Test deleting a user successfully.

        Verifies that delete_user calls the mocked delete_user function and prints
        a success message when the operation returns True.
        """
        self.mock_user_funcs["delete_user"].return_value = True
        menu.delete_user()
        mock_print.assert_called_once_with("User was successfully deleted.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1"])
    def test_delete_user_failure(self, mock_input, mock_print):
        """Test deleting a user when the operation fails.

        Verifies that delete_user calls the mocked delete_user function and prints
        an error message when the operation returns False.
        """
        self.mock_user_funcs["delete_user"].return_value = False
        menu.delete_user()
        self.assertTrue(any("An error occurred" in call[0][0]
                            for call in mock_print.call_args_list))

    # -------- STATUS --------
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["s1", "u1", "text"])
    def test_add_status_success(self, mock_input, mock_print):
        """Test adding a status successfully.

        Verifies that add_status calls the mocked add_status function and prints
        a success message when the operation returns True.
        """
        self.mock_status_funcs["add_status"].return_value = True
        menu.add_status()
        mock_print.assert_called_once_with("New status was successfully added.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["s1", "u1", "text"])
    def test_add_status_failure(self, mock_input, mock_print):
        """Test adding a status when the operation fails.

        Verifies that add_status calls the mocked add_status function and prints
        an error message when the operation returns False.
        """
        self.mock_status_funcs["add_status"].return_value = False
        menu.add_status()
        self.assertTrue(any("An error occurred" in call[0][0]
                            for call in mock_print.call_args_list))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["s1", "text"])
    def test_update_status_success(self, mock_input, mock_print):
        """Test updating a status successfully.

        Verifies that update_status calls the mocked modify_status function and
        prints a success message when the operation returns True.
        """
        self.mock_status_funcs["modify_status"].return_value = True
        menu.update_status()
        mock_print.assert_called_once_with("Status was successfully updated.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["s1", "text"])
    def test_update_status_failure(self, mock_input, mock_print):
        """Test updating a status when the operation fails.

        Verifies that update_status calls the mocked modify_status function and
        prints an error message when the operation returns False.
        """
        self.mock_status_funcs["modify_status"].return_value = False
        menu.update_status()
        self.assertTrue(any("An error occurred" in call[0][0]
                            for call in mock_print.call_args_list))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["s1"])
    def test_search_status_found(self, mock_input, mock_print):
        """Test searching for an existing status.

        Verifies that search_status calls the mocked search_status function and
        prints the status details when a status is found.
        """
        self.mock_status_funcs["search_status"].return_value = {
            "status_id": "s1", "user_id": "u1", "status_text": "text"
        }
        menu.search_status()
        self.assertTrue(any("Status ID: s1" in call[0][0]
                            for call in mock_print.call_args_list))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["s1"])
    def test_search_status_not_found(self, mock_input, mock_print):
        """Test searching for a non-existent status.

        Verifies that search_status calls the mocked search_status function and
        prints an error message when no status is found.
        """
        self.mock_status_funcs["search_status"].return_value = None
        menu.search_status()
        mock_print.assert_called_once_with("ERROR: Status does not exist.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["s1"])
    def test_delete_status_success(self, mock_input, mock_print):
        """Test deleting a status successfully.

        Verifies that delete_status calls the mocked delete_status function and
        prints a success message when the operation returns True.
        """
        self.mock_status_funcs["delete_status"].return_value = True
        menu.delete_status()
        mock_print.assert_called_once_with("Status was successfully deleted.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["s1"])
    def test_delete_status_failure(self, mock_input, mock_print):
        """Test deleting a status when the operation fails.

        Verifies that delete_status calls the mocked delete_status function and
        prints an error message when the operation returns False.
        """
        self.mock_status_funcs["delete_status"].return_value = False
        menu.delete_status()
        self.assertTrue(any("An error occurred" in call[0][0]
                            for call in mock_print.call_args_list))
        
        # -------- PICTURES --------

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1", "#car #sports"])
    @patch("menu.main.add_picture", return_value=True)
    def test_add_picture_success(self, mock_add, mock_input, mock_print):
        """Test adding a picture successfully via menu."""
        menu.add_picture()
        mock_add.assert_called_once_with("u1", "#car #sports")
        mock_print.assert_called_once_with("Picture successfully added.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1", "#car #sports"])
    @patch("menu.main.add_picture", return_value=False)
    def test_add_picture_failure(self, mock_add, mock_input, mock_print):
        """Test adding a picture when main.add_picture fails."""
        menu.add_picture()
        mock_print.assert_called_once_with("An error occurred while trying to add picture.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1"])
    @patch("menu.main.list_user_images", return_value=[("u1", "p1", "0001.png")])
    def test_list_user_images_success(self, mock_list, mock_input, mock_print):
        """Test listing user images successfully."""
        menu.list_user_images()
        mock_list.assert_called_once_with("u1")
        self.assertTrue(any("0001.png" in call[0][0] for call in mock_print.call_args_list))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1"])
    @patch("menu.main.list_user_images", return_value=[])
    def test_list_user_images_none(self, mock_list, mock_input, mock_print):
        """Test listing user images when none exist."""
        menu.list_user_images()
        mock_list.assert_called_once_with("u1")
        mock_print.assert_called_once_with("No images found for this user.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["u1"])
    @patch("menu.main.reconcile_images", return_value=(set(["missing.png"]), set()))
    def test_reconcile_images_reports_missing(self, mock_reconcile, mock_input, mock_print):
        """Test reconcile_images when files are missing on disk."""
        menu.reconcile_user_images()
        mock_reconcile.assert_called_once_with("u1")
        self.assertTrue(any("missing.png" in str(call) for call in mock_print.call_args_list))

    # -------- MENU FLOW --------
    @patch("sys.exit", side_effect=SystemExit)
    def test_quit_program(self, mock_exit):
        """Test the quit_program function.

        Verifies that quit_program calls sys.exit and raises SystemExit.
        """
        with self.assertRaises(SystemExit):
            menu.quit_program()
        mock_exit.assert_called_once()

    @patch("builtins.input", side_effect=["X", "Q"])
    @patch("builtins.print")
    @patch("menu.quit_program", side_effect=SystemExit)
    def test_run_menu_invalid_then_quit(self, mock_quit, mock_print, mock_input):
        """Test run_menu with an invalid option followed by quitting.

        Verifies that run_menu prints "Invalid option." for an invalid input and
        calls quit_program when 'Q' is entered, raising SystemExit.
        """
        with self.assertRaises(SystemExit):
            menu.run_menu()
        mock_print.assert_any_call("Invalid option.")
        mock_quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()