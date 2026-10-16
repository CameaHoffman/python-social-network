"""
Create the SQLite database and initialize Users/Status tables
using functional DataSet approach.
"""

import logging
from socialnetwork_model import make_dataset, init_schema

logger = logging.getLogger(__name__)

def main():
    """Create the database file and tables if they don’t exist."""
    ds = make_dataset()   # defaults to sqlite:///social_network.db
    init_schema(ds)
    print("Database and tables created.")

if __name__ == "__main__":
    main()
