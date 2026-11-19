
from pathlib import Path
import os

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Required environment variable is missing: {name}"
        )

    return value


DB_USER = get_required_env("POSTGRES_USER")
DB_PASSWORD = get_required_env("POSTGRES_PASSWORD")
DB_NAME = get_required_env("POSTGRES_DB")

DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
