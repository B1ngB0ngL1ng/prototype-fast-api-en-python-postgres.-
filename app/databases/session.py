from sqlalchemy.orm import sessionmaker
from app.databases.connection import engine

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
def get_db():
    with SessionLocal() as db:
        yield db
