
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.warehouse_service import WarehouseService


class WarehouseController:

    def __init__(self, db: Session):
        self.service = WarehouseService(db)

    def get_all(self):
        return self.service.get_all_warehouses()

    def get_by_id(self, warehouse_id: int):
        warehouse = self.service.get_warehouse(warehouse_id)

        if warehouse is None:
            raise HTTPException(
                status_code=404,
                detail="Warehouse not found"
            )

        return warehouse
