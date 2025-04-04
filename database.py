from urllib.request import localhost

from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker, declarative_base

# DB 연결 정보
#DATABASE_URL = "postgresql://wan:4553@localhost/postgres" mac

DATABASE_URL= "postgresql://postgres:4553@localhost:5432/postgres"





engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()