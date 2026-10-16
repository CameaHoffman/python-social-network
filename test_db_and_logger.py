"""
Name: Camea Hoffman
Assignment: a09
Description: Focused coverage tests for db_manager.py and logger_decorator.py
"""

import logging
import pytest
from db_manager import DatabaseManager
from logger_decorator import log_decorator


# --- db_manager.py tests ---

def test_db_manager_basic_context(tmp_path):
    """DatabaseManager should enter/exit cleanly with a valid SQLite DB."""
    db_file = tmp_path / "basic.db"
    db_url = f"sqlite:///{db_file}"
    with DatabaseManager(db_url) as db:
        assert hasattr(db, "tables")
    assert db_file.exists()


def test_db_manager_context_with_exception(tmp_path):
    """DatabaseManager should still exit cleanly if exception is raised."""
    db_file = tmp_path / "fail.db"
    db_url = f"sqlite:///{db_file}"
    with pytest.raises(RuntimeError):
        with DatabaseManager(db_url):
            raise RuntimeError("forced failure")
    assert db_file.exists()


# --- logger_decorator.py tests ---

def test_log_decorator_success_logs(caplog):
    """log_decorator should log function name on success."""
    @log_decorator
    def add(x, y):
        return x + y

    with caplog.at_level(logging.INFO):
        result = add(2, 3)

    assert result == 5
    assert any("add" in msg for msg in caplog.text.splitlines())


def test_log_decorator_exception_logs(caplog):
    """log_decorator should log function name and exception on failure."""
    @log_decorator
    def fail():
        raise ValueError("boom")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            fail()

    logs = caplog.text.splitlines()
    assert any("fail" in msg for msg in logs)
    assert any("boom" in msg for msg in logs)
