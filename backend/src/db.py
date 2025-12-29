"""Database connection and session management."""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel

from .utils.logger import get_logger

logger = get_logger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/todo_db"
)

# Convert postgresql:// to postgresql+asyncpg:// for async support
# Also handle sslmode parameter which asyncpg doesn't support directly
import ssl as ssl_module
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

parsed = urlparse(DATABASE_URL)
query_params = parse_qs(parsed.query)
ssl_required = "sslmode" in query_params and query_params["sslmode"][0] in ["require", "verify-ca", "verify-full"]

# Remove sslmode from query params as asyncpg doesn't support it
if "sslmode" in query_params:
    del query_params["sslmode"]

# Rebuild URL without sslmode
new_query = urlencode(query_params, doseq=True)
DATABASE_URL = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Create async engine with appropriate settings for database type
is_sqlite = "sqlite" in DATABASE_URL
engine_kwargs = {
    "echo": False,  # Set to True for debugging
}

# PostgreSQL-specific settings
if not is_sqlite:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    })
    # Handle SSL for asyncpg
    if ssl_required:
        ssl_context = ssl_module.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl_module.CERT_NONE
        engine_kwargs["connect_args"] = {"ssl": ssl_context}

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    """Dependency for getting database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("database_transaction_committed")
        except SQLAlchemyError as e:
            await session.rollback()
            # Log database errors with context (without sensitive data)
            logger.error(
                "database_error",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise
        except Exception as e:
            await session.rollback()
            # Log unexpected errors
            logger.error(
                "unexpected_database_error",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise
        finally:
            await session.close()


async def drop_old_user_table():
    """
    Drop old 'user' table if it exists.

    This is needed because the backend previously created a 'user' table
    with a different schema than Better Auth expects.
    """
    try:
        logger.info("checking_for_old_user_table")
        async with engine.begin() as conn:
            # Check if user table exists and has old schema (password_hash column)
            check_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'user'
                AND column_name = 'password_hash'
            """)
            result = await conn.execute(check_query)
            old_table_exists = result.scalar_one_or_none()

            if old_table_exists:
                logger.info("dropping_old_user_table")
                # Drop the old user table
                await conn.execute(text("DROP TABLE IF EXISTS user CASCADE"))
                logger.info("old_user_table_dropped")
    except Exception as e:
        # Log but don't fail startup if this fails
        logger.warning(
            "failed_to_drop_old_user_table",
            error=str(e),
            error_type=type(e).__name__,
        )


async def create_tables():
    """
    Create database tables for application.

    NOTE: Better Auth creates and manages its own tables:
    - user (id, email, name, emailVerified, image, createdAt, updatedAt)
    - session (id, userId, token, expiresAt, ipAddress, userAgent)
    - account (id, userId, providerId, accountId, providerType, etc.)
    - verification (id, identifier, value, expiresAt)

    This function only creates 'tasks' table and does NOT drop existing tables.
    """
    try:
        # First drop old user table if it exists
        await drop_old_user_table()

        logger.info("creating_database_tables")
        async with engine.begin() as conn:
            # Only create tasks table - don't drop anything!
            # Better Auth manages user, session, account, verification tables
            await conn.run_sync(SQLModel.metadata.create_all, checkfirst=True)
        logger.info("database_tables_created_successfully")
    except SQLAlchemyError as e:
        logger.error(
            "failed_to_create_tables",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise


async def close_connection():
    """Close database connection."""
    try:
        logger.info("closing_database_connection")
        await engine.dispose()
        logger.info("database_connection_closed")
    except Exception as e:
        logger.error(
            "failed_to_close_database_connection",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise
