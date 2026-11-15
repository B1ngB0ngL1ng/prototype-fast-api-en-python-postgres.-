
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Basisklasse voor alle SQLAlchemy-modellen.

    Alle database-modellen erven van deze klasse.
    """
    pass
