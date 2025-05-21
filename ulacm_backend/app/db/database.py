# File: ulacm_backend/app/db/database.py
# Purpose: Database engine and session management.

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create an async engine instance
# The URL is taken from the settings object, which assembles it
engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True, # Enable sending a PING to the server before using a connection
    # !!! TODO: Change in PRODUCTION !!!
    echo=True, # Set to True for debugging SQL queries
)

# Create a sessionmaker instance for creating AsyncSession objects
# expire_on_commit=False allows objects to be accessed after commit
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """
    Dependency to get a database session.
    Ensures the session is closed after the request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """
    Initialize the database tables.
    This should be called once during application startup if tables don't exist.
    For production, migrations (e.g., Alembic) are recommended.
    """
    async with engine.begin() as conn:
        # Import all models here so that Base knows about them
        from app.db.base_class import Base # noqa
        from app.db.models.team import Team # noqa
        from app.db.models.content_item import ContentItem # noqa
        from app.db.models.content_version import ContentVersion # noqa
        # Create all tables in the database.
        # await conn.run_sync(Base.metadata.drop_all) # Uncomment to drop tables first
        await conn.run_sync(Base.metadata.create_all)
