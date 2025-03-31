import uuid
from datetime import datetime
from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    published_at = Column(TIMESTAMP, nullable=False)
    summary = Column(Text)
    sentiment = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)