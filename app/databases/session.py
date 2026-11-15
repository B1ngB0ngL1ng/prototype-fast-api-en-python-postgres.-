
from sqlalchemy.orm import Session, sessionmaker

from app.databases.connection import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db():
    """
    Maakt een database-sessie voor een API-request.

    De sessie wordt na het request automatisch gesloten.
    """
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()
