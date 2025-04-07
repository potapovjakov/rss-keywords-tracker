from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List

from app.database import Base

class RSSSource(Base):
    __tablename__ = "rss_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    
    news = relationship("News", back_populates="source")

class Keyword(Base):
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True)
    
    news = relationship("NewsKeyword", back_populates="keyword")

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    url = Column(String, unique=True, index=True)
    published_date = Column(DateTime, index=True)
    source_id = Column(Integer, ForeignKey("rss_sources.id"))
    
    source = relationship("RSSSource", back_populates="news")
    keywords = relationship("NewsKeyword", back_populates="news")

class NewsKeyword(Base):
    __tablename__ = "news_keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"))
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    
    news = relationship("News", back_populates="keywords")
    keyword = relationship("Keyword", back_populates="news")

class RSSSourceBase(BaseModel):
    name: str
    url: HttpUrl

class RSSSourceCreate(RSSSourceBase):
    pass

class RSSSourceResponse(RSSSourceBase):
    id: int
    
    class Config:
        from_attributes = True

class KeywordBase(BaseModel):
    word: str

class KeywordCreate(KeywordBase):
    pass

class KeywordResponse(KeywordBase):
    id: int
    
    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    title: str
    content: str
    url: HttpUrl
    published_date: datetime
    source_id: int

class NewsResponse(NewsBase):
    id: int
    source: RSSSourceResponse
    keywords: List[KeywordResponse] = []
    
    class Config:
        from_attributes = True
