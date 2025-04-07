from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any

from app.models import RSSSource, Keyword, News, NewsKeyword
from app.models import RSSSourceCreate, KeywordCreate


def get_rss_sources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(RSSSource).offset(skip).limit(limit).all()

def create_rss_source(db: Session, source: RSSSourceCreate):
    existing_source = db.query(RSSSource).filter(
        (RSSSource.name == source.name) | (RSSSource.url == str(source.url))
    ).first()

    if existing_source:
        raise HTTPException(status_code=400, detail="RSS source already exists")

    db_source = RSSSource(name=source.name, url=str(source.url))
    db.add(db_source)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="RSS source already exists")
    db.refresh(db_source)
    return db_source


def get_rss_source(db: Session, source_id: int):
    return db.query(RSSSource).filter(RSSSource.id == source_id).first()

def delete_rss_source(db: Session, source_id: int):
    source = db.query(RSSSource).filter(RSSSource.id == source_id).first()
    if source:
        db.delete(source)
        db.commit()
        return True
    return False

def get_keywords(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Keyword).offset(skip).limit(limit).all()

def create_keyword(db: Session, keyword: KeywordCreate):
    existing_keyword = db.query(Keyword).filter(
        Keyword.word == keyword.word.lower()
    ).first()

    if existing_keyword:
        raise HTTPException(status_code=400, detail="Keyword already exists")

    db_keyword = Keyword(word=keyword.word)
    db.add(db_keyword)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Keyword already exists")
    db.refresh(db_keyword)
    return db_keyword

def get_keyword(db: Session, keyword_id: int):
    return db.query(Keyword).filter(Keyword.id == keyword_id).first()

def delete_keyword(db: Session, keyword_id: int):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if keyword:
        db.delete(keyword)
        db.commit()
        return True
    return False

def get_news(db: Session, skip: int = 0, limit: int = 100, keyword_id: Optional[int] = None):
    """
    Получение списка новостей с возможностью фильтрации по ключевому слову.
    """
    query = db.query(News)

    query = query.options(joinedload(News.source))

    if keyword_id:
        query = query.join(NewsKeyword).filter(NewsKeyword.keyword_id == keyword_id)

    query = query.order_by(News.published_date.desc())

    news_list = query.offset(skip).limit(limit).all()

    return news_list

def create_news(db: Session, news_data: Dict[str, Any], source_id: int, keywords_ids: List[int]):
    db_news = News(
        title=news_data["title"],
        content=news_data["content"],
        url=news_data["url"],
        published_date=news_data["published_date"],
        source_id=source_id
    )
    db.add(db_news)
    db.commit()
    db.refresh(db_news)

    for keyword_id in keywords_ids:
        news_keyword = NewsKeyword(news_id=db_news.id, keyword_id=keyword_id)
        db.add(news_keyword)

    db.commit()
    return db_news

def get_news_by_url(db: Session, url: str):
    return db.query(News).filter(News.url == url).first()

def get_keyword_by_id(db: Session, keyword_id: int):
    return db.query(Keyword).filter(Keyword.id == keyword_id).first()
