"""
=============================================================================
RECOVEREASE - DATABASE ENGINE & CONNECTION INTEGRATION (database.py)
=============================================================================
This module configures the database connection pool, session manager, and
ORM declarative base using SQLAlchemy.

DBMS ARCHITECTURAL CONCEPTS:
-----------------------------------------------------------------------------
1. Connection String / URI:
   Specifies the database dialect, network host, port, credentials, and database:
   - PostgreSQL: postgresql+psycopg://<user>:<password>@<host>:<port>/<dbname>
   - SQLite Fallback: sqlite:///<absolute_path_to_db_file>

2. Connection Pooling (Engine):
   Maintains a pool of reusable TCP connections to the DBMS to avoid the
   overhead of re-establishing handshakes on every HTTP request.
   - `pool_pre_ping=True`: Tests connections before issuing queries to discard
     dead or timed-out sockets.

3. Session Management (Unit of Work Pattern):
   - `SessionLocal`: Factory producing isolated transaction sessions.
   - `autocommit=False`: Ensures queries are wrapped inside explicit transactions
     following ACID principles until `db.commit()` is called.

4. Base (Declarative Metadata Registry):
   Maintains table metadata catalog used by `Base.metadata.create_all()` to
   generate DDL statements (`CREATE TABLE`, `CREATE INDEX`).
=============================================================================
"""

import os
import socket
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Locate and load environment variables from project .env
BACKEND_DIR = Path(__file__).resolve().parent.parent
env_path = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Default to PostgreSQL connection string from environment
RAW_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/recoverease"
)

# Unified SQLite fallback database file located in backend/ directory
UNIFIED_SQLITE_PATH = (BACKEND_DIR / "hostelos.db").as_posix()


def is_postgres_available(url_str: str) -> bool:
    """
    Performs a fast socket probe (1.0s timeout) to verify whether the
    PostgreSQL service is currently running on the designated host:port.
    Avoids long OS socket hang timeouts if PostgreSQL is stopped.
    """
    try:
        clean_url = (
            url_str.replace("postgresql+psycopg://", "http://")
                   .replace("postgresql://", "http://")
        )
        parsed = urlparse(clean_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except Exception:
        return False


# 2. Select Database Driver & Dialect
DATABASE_URL = RAW_DATABASE_URL
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration: allow multi-threaded access for FastAPI async workers
    connect_args = {"check_same_thread": False}
else:
    # Check if PostgreSQL service is reachable
    if is_postgres_available(DATABASE_URL):
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
        elif DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        print(f"[DBMS] Connected to PostgreSQL: {DATABASE_URL.split('@')[-1]}")
    else:
        # Seamlessly fallback to unified SQLite database file
        DATABASE_URL = f"sqlite:///{UNIFIED_SQLITE_PATH}"
        connect_args = {"check_same_thread": False}
        print(f"[DBMS] PostgreSQL offline -> Using SQLite at: {UNIFIED_SQLITE_PATH}")

# 3. Create SQLAlchemy Engine (Connection Pool Manager)
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Test connection validity before checkout
)

# 4. Create Session Factory
# autocommit=False ensures explicit transaction demarcation (ACID compliance)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# 5. Declarative Base (Catalog of all mapped entities)
Base = declarative_base()


# 6. Dependency Injection Session Provider
def get_db():
    """
    FastAPI dependency that provides an isolated SQLAlchemy database session
    for each incoming HTTP request.

    Guarantees:
      - The session is opened at request start.
      - The session is closed in the `finally` block when the request finishes,
        releasing the connection back to the pool to prevent connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
