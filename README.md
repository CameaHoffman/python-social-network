# Python Social Network

A Python social networking project by Camea Hoffman, developed across lessons
in Python 320. This repository starts with my assignment 10 implementation.

## Features

- Manage users and status updates through a command-line menu.
- Store data in SQLite using Peewee DataSet.
- Import users and status updates from CSV files.
- Track image metadata and tagged folder structures.
- Expose Flask API endpoints at `/users`, `/images`, and `/differences`.
- Include the original unit tests.

## Local setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install Flask-RESTful pytest
python create_db.py
python menu.py
```

Run `python api.py` to start the local Flask API. The original requirements file
is preserved; Flask-RESTful and pytest are installed separately above because
the coursework requirements file does not list them.

## Project status

The first commit preserves my coursework Python files and tests unchanged.
This is a coursework baseline, with further cleanup and improvements to come.
The tests and application have not been verified for this baseline's current
dependency versions. Image scanning and reconciliation have known inconsistencies.
The API has no authentication and runs in debug mode when launched directly;
it is intended for local use with sample data.

Course datasets, generated logs, databases, instructor assignment instructions,
and the original classroom Git history are not included.
