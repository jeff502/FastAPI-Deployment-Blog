from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


# +aiosqlite tells sqlite what driver to use
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"  # current dir/blog.db

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },  # SQLite specific since it doesn't support multiple threads
)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Factory that creates sessions. Autocommit and Autoflush to false is standard FastAPI pattern.

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:  # Context manager to handle tear downs
        yield session
