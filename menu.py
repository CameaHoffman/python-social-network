"""
Name: Camea Hoffman
Assignment: a09
Description: Menu providing basic front end for the functional social networking project.

This module provides a command-line interface for the social networking application.
It allows users to:
- Load user and status data from CSV files
- Add, update, search, and delete users and statuses
- Add pictures with tags and list user images
- Quit the program

The menu interacts with functions in main.py, uses global user_funcs and
status_funcs dictionaries for operation delegation, and relies on logging
to track application activity and errors.
"""

import sys
import logging
import main

# pylint: disable=invalid-name
# pylint: disable=global-statement

# Global closure dicts
user_funcs = None
status_funcs = None

LOG_FILENAME = "socialnetwork.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    filemode="a",
    format="%(asctime)s %(levelname)s: %(message)s"
)


# --- Menu actions ---
def load_users():
    """Load user data from a CSV file into the database.

    Prompts the user for a filename, calls main.load_users to process the file,
    and prints a success or failure message. Logs the start of the operation.

    Side effects:
        Prints a success or failure message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Loading user database started")
    filename = input("Enter filename of user file: ")
    if main.load_users(filename, user_funcs):
        print("User database loaded successfully.")
    else:
        print("Failed to load user database. Please check the file format.")


def load_status_updates():
    """Load status updates from a CSV file into the database.

    Prompts the user for a filename, calls main.load_status_updates to process
    the file, and prints a success or failure message. Logs the start of the
    operation.

    Side effects:
        Prints a success or failure message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Loading status updates started")
    filename = input("Enter filename for status file: ")
    if main.load_status_updates(filename, status_funcs):
        print("User status database loaded successfully.")
    else:
        print("Failed to load status database. Please check the file format.")


def add_user():
    """Add a new user to the database.

    Prompts the user for user_id, email, user_name, and user_last_name, calls
    main.add_user to add the user, and prints a success or failure message.
    Logs the start of the operation.

    Side effects:
        Prints a success or failure message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Adding user function started")
    user_id = input("User ID: ")
    email = input("User email: ")
    user_name = input("User name: ")
    user_last_name = input("User last name: ")
    if not main.add_user(user_id, email, user_name, user_last_name, user_funcs):
        print("An error occurred while trying to add new user.")
    else:
        print("User was successfully added.")


def update_user():
    """Update an existing user's details in the database.

    Prompts the user for user_id, email, user_name, and user_last_name, calls
    main.update_user to update the user, and prints a success or failure message.
    Logs the start of the operation.

    Side effects:
        Prints a success or failure message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Updating user function started")
    user_id = input("User ID: ")
    email = input("User email: ")
    user_name = input("User name: ")
    user_last_name = input("User last name: ")
    if not main.update_user(user_id, email, user_name, user_last_name, user_funcs):
        print("An error occurred while trying to update user.")
    else:
        print("User was successfully updated.")


def search_user():
    """Search for a user by user_id in the database.

    Prompts the user for a user_id, calls main.search_user to retrieve the user,
    and prints the user's details (user_id, email, user_name, user_last_name) if
    found, or an error message if not found. Logs the start of the operation.

    Side effects:
        Prints user details or an error message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Searching user function started")
    user_id = input("Enter user ID to search: ")
    result = main.search_user(user_id, user_funcs)
    if result is None:
        print("ERROR: User does not exist.")
    else:
        print(f"User ID: {result['user_id']}")
        print(f"Email: {result['email']}")
        print(f"Name: {result['user_name']}")
        print(f"Last name: {result['user_last_name']}")


def delete_user():
    """Delete a user from the database.

    Prompts the user for a user_id, calls main.delete_user to delete the user,
    and prints a success or failure message. Logs the start of the operation.

    Side effects:
        Prints a success or failure message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Deleting user function started")
    user_id = input("User ID: ")
    if not main.delete_user(user_id, user_funcs):
        print("An error occurred while trying to delete user.")
    else:
        print("User was successfully deleted.")


def add_status():
    """Add a new status to the database.

    Prompts the user for status_id, user_id, and status_text, calls
    main.add_status to add the status, and prints a success or failure message.
    Logs the start of the operation.

    Side effects:
        Prints a success or failure message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Adding status function started")
    status_id = input("Status ID: ")
    user_id = input("User ID: ")
    status_text = input("Status text: ")
    if not main.add_status(status_id, user_id, status_text, status_funcs):
        print("An error occurred while trying to add new status.")
    else:
        print("New status was successfully added.")


def update_status():
    """Update an existing status's text in the database.

    Prompts the user for status_id and status_text, calls main.update_status to
    update the status, and prints a success or failure message. Logs the start
    of the operation.

    Side effects:
        Prints a success or failure message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Updating status function started")
    status_id = input("Status ID: ")
    status_text = input("Status text: ")
    if not main.update_status(status_id, status_text, status_funcs):
        print("An error occurred while trying to update status.")
    else:
        print("Status was successfully updated.")


def search_status():
    """Search for a status by status_id in the database.

    Prompts the user for a status_id, calls main.search_status to retrieve the
    status, and prints the status details (status_id, user_id, status_text) if
    found, or an error message if not found. Logs the start of the operation.

    Side effects:
        Prints status details or an error message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Searching status function started")
    status_id = input("Enter status ID to search: ")
    result = main.search_status(status_id, status_funcs)
    if result is None:
        print("ERROR: Status does not exist.")
    else:
        print(f"Status ID: {result['status_id']}")
        print(f"User ID: {result['user_id']}")
        print(f"Status text: {result['status_text']}")


def delete_status():
    """Delete a status from the database.

    Prompts the user for a status_id, calls main.delete_status to delete the
    status, and prints a success or failure message. Logs the start of the
    operation.

    Side effects:
        Prints a success or failure message to the console.
        Logs the operation start to socialnetwork.log.
    """
    logging.info("Deleting status function started")
    status_id = input("Status ID: ")
    if not main.delete_status(status_id, status_funcs):
        print("An error occurred while trying to delete status.")
    else:
        print("Status was successfully deleted.")

def add_picture():
    """Add a new picture to the database and filesystem.

    Prompts for user_id and tags, then calls main.add_picture.
    """
    logging.info("Adding picture function started")
    user_id = input("User ID: ")
    tags = input("Enter tags (space-separated, e.g. #car #sports): ")
    if not main.add_picture(user_id, tags):
        print("An error occurred while trying to add picture.")
    else:
        print("Picture successfully added.")


def list_user_images():
    """List all images for a given user.

    Prompts for user_id, then calls main.list_user_images.
    """
    logging.info("Listing user images function started")
    user_id = input("User ID: ")
    images = main.list_user_images(user_id)
    if not images:
        print("No images found for this user.")
    else:
        for img in images:
            print(img)

def reconcile_user_images():
    """Reconcile images between DB and filesystem for a user."""
    logging.info("Reconciling images started")
    user_id = input("User ID: ")
    missing_on_disk, missing_in_db = main.reconcile_images(user_id)

    print("\n--- Reconciliation Report ---")
    if missing_on_disk:
        print("Images in DB but missing on disk:")
        for pic in missing_on_disk:
            print("  ", pic)
    else:
        print("No DB-only images.")

    if missing_in_db:
        print("Images on disk but missing in DB:")
        for pic in missing_in_db:
            print("  ", pic)
    else:
        print("No disk-only images.")

def quit_program():
    """Exit the program.

    Logs the start of the quit operation and terminates the program using
    sys.exit.

    Side effects:
        Logs the operation start to socialnetwork.log.
        Terminates the program.

    Raises:
        SystemExit: Always raised to exit the program.
    """
    logging.info("Quitting program function started")
    sys.exit()


# --- Main Menu ---
def run_menu():
    """Run the main menu loop for the social networking application.

    Initializes global user_funcs and status_funcs by calling
    main.init_user_functions and main.init_status_functions, then enters a loop
    prompting the user to select menu options (A, B, C, ..., J, Q). Executes the
    corresponding function for valid options (case-insensitive) or prints an
    error message for invalid options. Logs the start of the menu.

    Side effects:
        Initializes global user_funcs and status_funcs.
        Prints the menu and user prompts to the console.
        Logs the menu start to socialnetwork.log.
    """
    logging.info("Running menu started")
    global user_funcs, status_funcs
    user_funcs = main.init_user_functions()
    status_funcs = main.init_status_functions()

    menu_options = {
        "A": load_users,
        "B": load_status_updates,
        "C": add_user,
        "D": update_user,
        "E": search_user,
        "F": delete_user,
        "G": add_status,
        "H": update_status,
        "I": search_status,
        "J": delete_status,
        "K": add_picture,
        "L": list_user_images,
        "M": reconcile_user_images,
        "Q": quit_program,
    }


    while True:
        user_selection = input("""
                            A: Load user database
                            B: Load status database
                            C: Add user
                            D: Update user
                            E: Search user
                            F: Delete user
                            G: Add status
                            H: Update status
                            I: Search status
                            J: Delete status
                            K: Add picture
                            L: List user images
                            M: Reconcile user images
                            Q: Quit

                            Please enter your choice: """).strip()
        if user_selection.upper() in menu_options:
            menu_options[user_selection.upper()]()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    run_menu()
