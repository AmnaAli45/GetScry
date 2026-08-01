from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite - ek simple file database
DATABASE_URL = "sqlite:///./getscry.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}   # SQLite ke liye zaroori hai FastAPI mein
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()