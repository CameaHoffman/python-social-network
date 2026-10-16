"""
Name: Camea Hoffman
Assignment: a09
Description: Context manager for database connections.

This module defines the DatabaseManager class, which wraps a Peewee
DataSet connection in a context manager. It ensures the connection is
opened when entering the block and properly closed when exiting.
"""

from playhouse.dataset import DataSet


class DatabaseManager:
    """
    Context manager for managing Peewee DataSet database connections.

    Example:
        >>> with DatabaseManager("sqlite:///social_network.db") as db:
        ...     users = db["Users"]
        ...     users.insert(user_id="u1", email="a@b.com",
        ...                   user_name="Alice", user_last_name="Smith")

    Attributes:
        db_url (str): Database connection string (e.g., sqlite:///file.db).
        ds (DataSet | None): Active DataSet connection, initialized on __enter__.
    """

    def __init__(self, db_url):
        """
        Initialize the DatabaseManager with a given database URL.

        Args:
            db_url (str): Connection string for the database.
        """
        self.db_url = db_url
        self.ds = None

    def __enter__(self):
        """
        Open a DataSet connection and return it for use within a context.

        Returns:
            DataSet: Active DataSet connection to the specified database.
        """
        self.ds = DataSet(self.db_url)
        return self.ds

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the DataSet connection when exiting the context.

        Args:
            exc_type (type): Exception type, if any was raised.
            exc_value (Exception): Exception instance, if any was raised.
            traceback (traceback): Traceback object, if any exception was raised.
        """
        if self.ds is not None:
            self.ds.close()
