from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import parse_obj_as

from config import logger
from app.database import get_db
from app.models import RSSSourceResponse, RSSSourceCreate, KeywordResponse, KeywordCreate, NewsResponse, KeywordBase
from app.crud import (
    get_rss_sources, create_rss_source, get_rss_source, delete_rss_source,
    get_keywords, create_keyword, get_keyword, delete_keyword,
    get_news, get_keyword_by_id
)
from app.scanner import scan_rss_feeds

# Создание роутера для API
router = APIRouter()

# Маршруты для RSS источников
@router.get("/sources", response_model=List[RSSSourceResponse])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sources = get_rss_sources(db, skip=skip, limit=limit)
    return sources

@router.post("/sources", response_model=RSSSourceResponse)
def create_source(source: RSSSourceCreate, db: Session = Depends(get_db)):
    return create_rss_source(db=db, source=source)

@router.get("/sources/{source_id}", response_model=RSSSourceResponse)
def read_source(source_id: int, db: Session = Depends(get_db)):
    db_source = get_rss_source(db, source_id=source_id)
    if db_source is None:
        raise HTTPException(status_code=404, detail="RSS source not found")
    return db_source

@router.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    success = delete_rss_source(db, source_id=source_id)
    if not success:
        raise HTTPException(status_code=404, detail="RSS source not found")
    return {"detail": "RSS source deleted"}

# Маршруты для ключевых слов
@router.get("/keywords", response_model=List[KeywordResponse])
def read_keywords(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    keywords = get_keywords(db, skip=skip, limit=limit)
    return keywords

@router.post("/keywords", response_model=KeywordResponse)
def create_keyword_route(keyword: KeywordCreate, db: Session = Depends(get_db)):
    return create_keyword(db=db, keyword=keyword)

@router.get("/keywords/{keyword_id}", response_model=KeywordResponse)
def read_keyword(keyword_id: int, db: Session = Depends(get_db)):
    db_keyword = get_keyword(db, keyword_id=keyword_id)
    if db_keyword is None:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return db_keyword

@router.delete("/keywords/{keyword_id}")
def delete_keyword_route(keyword_id: int, db: Session = Depends(get_db)):
    success = delete_keyword(db, keyword_id=keyword_id)
    if not success:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return {"detail": "Keyword deleted"}

# Маршруты для новостей
@router.get("/news", response_model=List[NewsResponse])
def read_news(skip: int = 0, limit: int = 20, keyword_id: Optional[int] = None, db: Session = Depends(get_db)):
    # Получаем новости из базы данных
    news_items = get_news(db, skip=skip, limit=limit, keyword_id=keyword_id)

    # Подготавливаем список для ответа API
    response_items = []

    for news in news_items:
        # Для каждой новости извлекаем ID ключевых слов из связи NewsKeyword
        keyword_ids = [nk.keyword_id for nk in news.keywords]

        # Получаем объекты Keyword по ID
        keywords = [get_keyword_by_id(db, kid) for kid in keyword_ids if kid is not None]

        # Создаем объект ответа
        news_dict = {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "url": news.url,
            "published_date": news.published_date,
            "source_id": news.source_id,
            "source": news.source,
            "keywords": keywords
        }

        response_items.append(news_dict)

    # Используем Pydantic для преобразования в формат ответа
    return parse_obj_as(List[NewsResponse], response_items)

# Маршрут для ручного запуска сканирования
@router.post("/scan")
def run_scan(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info("Запущено ручное сканирование RSS-лент")
    background_tasks.add_task(scan_rss_feeds, db)
    return {"detail": "Scan started in background"}
