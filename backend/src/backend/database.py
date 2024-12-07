import os
import platform
from pathlib import Path

from sqlalchemy import URL, create_engine

PG_HOST = os.getenv("PGHOST")
PG_DATABASE = os.getenv("PGDATABASE")
PG_USER = os.getenv("PGUSER")
PG_PASSWORD = os.getenv("PGPASSWORD")

engine = create_engine(
    url=URL.create(
        drivername="postgresql+psycopg",
        host=PG_HOST,
        database=PG_DATABASE,
        username=PG_USER,
        password=PG_PASSWORD,
        query={"sslmode": "require"},
    )
)
