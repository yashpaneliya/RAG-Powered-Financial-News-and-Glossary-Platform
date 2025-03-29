from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from core.logger import logger

PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
GLOSSARY_DB = os.getenv("GLOSSARY_DB")

GLOSSARY_DB_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{GLOSSARY_DB}"

try:
    logger.info("Connecting to postgres..")
    engine = create_engine(GLOSSARY_DB_URL)
    SessionLocal = sessionmaker(bind=engine, autoflush=False)
    logger.info("Connected to postgres")
except Exception as e:
    logger.error("Connection to postgres failed")

def get_db():
    db = SessionLocal()
    try:
        logger.info("Creating a new DB session")
        yield db
    except Exception as e:
        logger.error("Closing db session")
        db.close()