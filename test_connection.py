from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.databases.connection import engine


def main():
    try:
        with engine.connect() as connection:
            name = connection.execute(text("SELECT current_database()")).scalar_one()
        print(f"Verbinding geslaagd met database: {name}")
    except SQLAlchemyError as error:
        print(f"Databaseverbinding mislukt: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
