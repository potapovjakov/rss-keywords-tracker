import logging
from logging.handlers import RotatingFileHandler

DATABASE_URL = "sqlite:///./rss_tracker.db"
# Настройка периодичности сканирования лент
SCAN_INTERVAL_SECONDS = 60

LOG_FILE = "rss-tracker.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_MAX_SIZE = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 3

def setup_logging():
    logger = logging.getLogger("rss-tracker")
    logger.setLevel(LOG_LEVEL)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setLevel(LOG_LEVEL)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()
