from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.databases.session import get_db
from app.controllers.resource_controller import ResourceController
from app.security.auth import require_permission
from app.schemas.resource_schema import ResourceInput
from app.models.resource_models import RESOURCES

router = APIRouter(prefix="/api/v1")
PUBLIC = list(RESOURCES)[:12]  # original 12 public resources

def pagination(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    return limit, offset

def build_list(resource):
    def endpoint(page: tuple = Depends(pagination), db: Session = Depends(get_db)):
        return ResourceController(db, resource).list(*page)
    endpoint.__name__ = f"list_{resource}"
    return endpoint

def build_get(resource):
    def endpoint(id: int, db: Session = Depends(get_db)):
        return ResourceController(db, resource).get(id)
    endpoint.__name__ = f"get_{resource}"
    return endpoint

def build_post(resource):
    def endpoint(body: ResourceInput, db: Session = Depends(get_db)):
        return ResourceController(db, resource).create(body.model_dump(exclude_unset=True))
    endpoint.__name__ = f"create_{resource}"
    return endpoint

def build_put(resource):
    def endpoint(id: int, body: ResourceInput, db: Session = Depends(get_db)):
        return ResourceController(db, resource).update(id, body.model_dump(exclude_unset=True))
    endpoint.__name__ = f"update_{resource}"
    return endpoint

def build_delete(resource):
    def endpoint(id: int, db: Session = Depends(get_db)):
        ResourceController(db, resource).delete(id)
        return Response(status_code=204)
    endpoint.__name__ = f"delete_{resource}"
    return endpoint

for resource in PUBLIC:
    tag = resource.replace("_", " ").title()
    router.add_api_route(f"/{resource}", build_list(resource), methods=["GET"],
                         tags=[tag], dependencies=[Depends(require_permission(resource, "get"))])
    router.add_api_route(f"/{resource}/{{id}}", build_get(resource), methods=["GET"],
                         tags=[tag], dependencies=[Depends(require_permission(resource, "get"))])
    router.add_api_route(f"/{resource}", build_post(resource), methods=["POST"],
                         status_code=201, tags=[tag], dependencies=[Depends(require_permission(resource, "post"))])
    router.add_api_route(f"/{resource}/{{id}}", build_put(resource), methods=["PUT"],
                         tags=[tag], dependencies=[Depends(require_permission(resource, "put"))])
    router.add_api_route(f"/{resource}/{{id}}", build_delete(resource), methods=["DELETE"],
                         status_code=204, tags=[tag], dependencies=[Depends(require_permission(resource, "delete"))])

def add_child(path, parent, child, field):
    def endpoint(id: int, page: tuple = Depends(pagination), db: Session = Depends(get_db)):
        ResourceController(db, parent).get(id)
        return ResourceController(db, child).service.children(field, id, *page)
    endpoint.__name__ = f"{parent}_{child}_children"
    router.add_api_route(path, endpoint, methods=["GET"], tags=[parent.title()],
                         dependencies=[Depends(require_permission(parent, "get"))])

for path, parent, child, field in [
    ("/warehouses/{id}/locations", "warehouses", "locations", "warehouse_id"),
    ("/orders/{id}/items", "orders", "order_items", "order_id"),
    ("/clients/{id}/orders", "clients", "orders", "client_id"),
    ("/shipments/{id}/items", "shipments", "shipment_items", "shipment_id"),
    ("/transfers/{id}/items", "transfers", "transfer_items", "transfer_id"),
    ("/item_lines/{id}/items", "item_lines", "items", "item_line_id"),
    ("/item_groups/{id}/items", "item_groups", "items", "item_group_id"),
    ("/item_types/{id}/items", "item_types", "items", "item_type_id"),
    ("/suppliers/{id}/items", "suppliers", "items", "supplier_id"),
    ("/items/{id}/inventory", "items", "inventories", "item_id"),
    ("/shipments/{id}/orders", "shipments", "orders", "id"),
]:
    add_child(path, parent, child, field)

@router.get("/items/{id}/inventory/totals", tags=["Items"],
            dependencies=[Depends(require_permission("items", "get"))])
def item_inventory_totals(id: int, db: Session = Depends(get_db)):
    ResourceController(db, "items").get(id)
    records = ResourceController(db, "inventories").service.children("item_id", id, 500, 0)
    fields = ["quantity_on_hand", "quantity_expected", "quantity_ordered", "quantity_allocated"]
    return {"item_id": id, **{field: sum(int(x.get(field) or 0) for x in records) for field in fields}}

@router.get("/inventories/by-location/{item_id}/{location_id}", tags=["Inventories"],
            dependencies=[Depends(require_permission("inventories", "get"))])
def inventory_by_composite_key(item_id: int, location_id: int, db: Session = Depends(get_db)):
    rows = ResourceController(db, "inventories").service.children("item_id", item_id, 500, 0)
    record = next((x for x in rows if x.get("location_id") == location_id), None)
    if record is None:
        raise HTTPException(404, "Voorraadrecord niet gevonden")
    return record
