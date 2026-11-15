
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.repositories.warehouse_repository import WarehouseRepository


class WarehouseService:

    def __init__(self, db: Session):
        self.repository = WarehouseRepository(db)

    def get_all_warehouses(self) -> list[Warehouse]:
        return self.repository.get_all()

    def get_warehouse(self, warehouse_id: int) -> Warehouse | None:
        return self.repository.get_by_id(warehouse_id)
