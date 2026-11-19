
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from src.config import (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME,
)

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=2,
    pool_recycle=1800,
    connect_args={"connect_timeout": 10},
)


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT current_database(), current_user, version()
            """)
        )
        return result.fetchone()
