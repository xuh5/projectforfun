from __future__ import annotations

import os
from pathlib import Path
from typing import Generator
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Load environment variables from .env file
# Try loading from backend directory first, then project root
env_path = Path(__file__).parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Construct DATABASE_URL from Supabase environment variables if not directly provided
def get_database_url() -> str:
    """Get database URL from environment variables."""
    # If DATABASE_URL is directly provided, fix it if malformed
    db_url = os.getenv("DATABASE_URL")
    if db_url and ("postgresql://" in db_url or "postgres://" in db_url):
        # Work with the raw string to avoid urlparse() mangling it first
        # Format: postgresql://user:password@host:port/db
        # If password contains @, urlparse will break it
        
        # Find the scheme separator
        scheme_end = db_url.find("://")
        if scheme_end > 0:
            scheme = db_url[:scheme_end]
            rest = db_url[scheme_end + 3:]  # Everything after "://"
            
            # Find the path separator (/) if it exists
            path_start = rest.find("/")
            if path_start > 0:
                netloc_part = rest[:path_start]
                path_part = rest[path_start:]
            else:
                netloc_part = rest
                path_part = ""
            
            # Find the LAST @ in netloc_part (this is the real separator)
            # The password might contain @, so we need the last one
            last_at = netloc_part.rfind("@")
            if last_at > 0:
                creds = netloc_part[:last_at]
                host_port = netloc_part[last_at + 1:]
                
                # Check if credentials contain : (user:password format)
                if ":" in creds:
                    user, password = creds.split(":", 1)
                    # URL-encode the password (and user just in case)
                    encoded_user = quote_plus(user)
                    encoded_password = quote_plus(password)
                    
                    # Reconstruct the URL
                    fixed_url = f"{scheme}://{encoded_user}:{encoded_password}@{host_port}{path_part}"
                    return fixed_url
        
        # If we couldn't fix it, return as-is (might already be correct)
        return db_url
    elif db_url:
        return db_url
    
    # Otherwise, construct from Supabase environment variables
    db_host = os.getenv("SUPABASE_DB_HOST")
    # Default to transaction pooler port (6543) for free tier, or use 5432 for direct connection
    db_port = os.getenv("SUPABASE_DB_PORT", "6543")
    db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
    db_user = os.getenv("SUPABASE_DB_USER", "postgres")
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    
    if db_host and db_password:
        # URL-encode password to handle special characters like @, ], etc.
        encoded_password = quote_plus(db_password)
        encoded_user = quote_plus(db_user) if db_user else "postgres"
        return f"postgresql://{encoded_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
    
    # Fallback to SQLite for local development if Supabase vars not set
    from pathlib import Path
    return f"sqlite:///{Path(__file__).parent.parent / 'data' / 'graph.db'}"


DATABASE_URL = get_database_url()

# Log which database is being used (for debugging)
import logging
logger = logging.getLogger(__name__)
if "postgresql" in DATABASE_URL:
    # Mask password in log
    masked_url = DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else DATABASE_URL
    logger.info(f"✓ Connecting to Supabase PostgreSQL: postgresql://***@{masked_url}")
else:
    logger.warning(f"⚠ Using SQLite (fallback): {DATABASE_URL}")
    logger.warning("⚠ Make sure your .env file has SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD set!")

# Connection args - different for SQLite vs PostgreSQL
connect_args = {}
is_postgresql = "postgresql" in DATABASE_URL

if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
elif is_postgresql:
    # PostgreSQL-specific connection args
    # For transaction pooler (port 6543), use 'prefer' SSL mode
    # For direct connection (port 5432), use 'require' SSL mode
    db_port = os.getenv("SUPABASE_DB_PORT", "6543")
    if "6543" in DATABASE_URL or db_port == "6543":
        # Transaction pooler (free tier) - prefer SSL but don't require it
        connect_args = {
            "connect_timeout": 10,
            "sslmode": "prefer",
        }
    else:
        # Direct connection - require SSL
        connect_args = {
            "connect_timeout": 10,
            "sslmode": "require",
        }

# Build engine kwargs - only include pooling for PostgreSQL
engine_kwargs = {
    "connect_args": connect_args,
    "echo": os.getenv("DB_ECHO", "false").lower() == "true",
}

# Add PostgreSQL-specific pooling settings (don't pass None for SQLite)
if is_postgresql:
    pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    engine_kwargs.update({
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_pre_ping": True,  # Verify connections before using
    })

# Create engine with appropriate settings
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    from backend.database.models import Base
    from pathlib import Path

    # Create data directory if using SQLite
    if "sqlite" in DATABASE_URL:
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create all tables
    # Note: For production, prefer using Alembic migrations instead of create_all
    Base.metadata.create_all(bind=engine)

