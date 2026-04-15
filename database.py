from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings

# +aiosqlite tells sqlite what driver to use

# engine = create_async_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={
#         "check_same_thread": False
#     },  # SQLite specific since it doesn't support multiple threads
# )

engine = create_async_engine(settings.database_url)


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
