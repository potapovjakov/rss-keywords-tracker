from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL, logger

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    from app.models import RSSSource, Keyword, News, NewsKeyword
    Base.metadata.create_all(bind=engine)
    logger.info("База данных инициализирована")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
