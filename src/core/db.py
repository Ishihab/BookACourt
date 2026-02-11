from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.core.config import settings
import asyncpg


DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)

engine = create_async_engine(
    DATABASE_URL, 
    echo= (settings.ENVIRONMENT == "local"), 
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=600,
    connect_args={"ssl": "require"})

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

