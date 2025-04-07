import uvicorn
from fastapi import FastAPI

from config import logger
from app.database import init_db
from app.scanner import start_rss_scanner
from app.api import router

app = FastAPI(
    title="RSS Keywords Tracker",
    description="Сервис для отслеживания ключевых слов в RSS лентах",
    version="1.0.0"
)

app.include_router(router)

@app.on_event("startup")
def startup_event():
    logger.info("Запуск приложения RSS Keywords Tracker")
    init_db()
    start_rss_scanner()
    logger.info("Приложение успешно запущено")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Завершение работы приложения RSS Keywords Tracker")



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
