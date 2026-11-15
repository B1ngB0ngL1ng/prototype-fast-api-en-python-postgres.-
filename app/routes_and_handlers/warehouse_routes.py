
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.warehouse_controllers import WarehouseController
from app.databases.session import get_db
from app.schemas.warehouse_schema import WarehouseResponse


router = APIRouter(
    prefix="/api/v1/warehouses",
    tags=["Warehouses"]
)


@router.get("/", response_model=list[WarehouseResponse])
def get_warehouses(db: Session = Depends(get_db)):
    controller = WarehouseController(db)
    return controller.get_all()


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db)
):
    controller = WarehouseController(db)
    return controller.get_by_id(warehouse_id)
