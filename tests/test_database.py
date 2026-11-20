
import pytest

from src.database import engine, test_connection as get_connection_info


def test_database_connection():
    """Verify that Python can connect to the SupplyPulse database."""

    try:
        result = get_connection_info()

        assert result is not None
        assert result[0] == "supplypulse"
        assert result[1] == "supplypulse_user"
        assert "PostgreSQL" in result[2]

    finally:
        engine.dispose()
