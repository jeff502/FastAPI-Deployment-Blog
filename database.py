from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db" # current dir/blog.db

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # SQLite specific since it doesn't support multiple threads 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Factory that creates sessions. Autocommit and Autoflush to false is standard FastAPI pattern.


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db: # Context manager to handle tear downs
        yield db