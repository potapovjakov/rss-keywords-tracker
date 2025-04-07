import feedparser
import re
import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session

from config import SCAN_INTERVAL_SECONDS, logger
from app.database import SessionLocal
from app.crud import (get_rss_sources, get_keywords, create_news,
                      get_news_by_url)

def scan_rss_feeds(db: Session):
    """
    Функция для сканирования RSS лент и поиска ключевых слов в новостях
    """
    logger.info(f"Сканирование RSS лент начато в {datetime.now()}")

    sources = get_rss_sources(db)
    keywords = get_keywords(db)

    logger.info(f"Найдено {len(sources)} RSS источников и {len(keywords)} ключевых слов")

    keyword_dict = {keyword.word.lower(): keyword.id for keyword in keywords}

    for source in sources:
        try:
            logger.info(f"Сканирование источника: {source.name} ({source.url})")
            feed = feedparser.parse(source.url)

            if hasattr(feed, 'bozo_exception'):
                logger.warning(f"Проблема с парсингом RSS {source.url}: {feed.bozo_exception}")

            logger.info(f"Найдено {len(feed.entries)} записей в ленте {source.name}")

            for entry in feed.entries:
                existing_news = get_news_by_url(db, entry.link)
                if existing_news:
                    logger.debug(f"Новость уже существует: {entry.title}")
                    continue

                title = entry.title

                if hasattr(entry, 'content'):
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                else:
                    content = ""

                if hasattr(entry, 'published_parsed'):
                    published_date = datetime(*entry.published_parsed[:6])
                else:
                    published_date = datetime.now()

                matching_keywords = []
                text_to_check = f"{title.lower()} {content.lower()}"

                for word, keyword_id in keyword_dict.items():
                    if re.search(r'\b' + re.escape(word) + r'\b', text_to_check):
                        matching_keywords.append(keyword_id)
                        logger.info(f"Найдено ключевое слово '{word}' в новости: {title}")

                if matching_keywords:
                    news_data = {
                        "title": title,
                        "content": content,
                        "url": entry.link,
                        "published_date": published_date
                    }
                    create_news(db, news_data, source.id, matching_keywords)
                    logger.info(f"Сохранена новость: {title}")

        except Exception as e:
            logger.error(f"Ошибка при сканировании {source.url}: {str(e)}", exc_info=True)

    logger.info(f"Сканирование RSS лент завершено в {datetime.now()}")

def start_rss_scanner():
    """
    Функция для запуска сканера RSS лент в отдельном потоке
    """
    def run_scheduler():
        logger.info("Запущен сканер RSS-лент")
        while True:
            db = SessionLocal()
            try:
                scan_rss_feeds(db)
            except Exception as e:
                logger.error(f"Ошибка в работе сканера: {str(e)}", exc_info=True)
            finally:
                db.close()

            logger.info(f"Ожидание {SCAN_INTERVAL_SECONDS} секунд до следующего сканирования...")
            time.sleep(SCAN_INTERVAL_SECONDS)

    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    logger.info("Сканер RSS-лент запущен в отдельном потоке")
    return thread
