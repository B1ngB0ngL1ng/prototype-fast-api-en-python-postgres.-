
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse


class WarehouseRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Warehouse]:
        """
        Haal alle warehouses op uit PostgreSQL.
        """
        statement = select(Warehouse).order_by(Warehouse.id)

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_id(self, warehouse_id: int) -> Warehouse | None:
        """
        Haal één warehouse op aan de hand van het ID.
        """
        return self.db.get(Warehouse, warehouse_id)
