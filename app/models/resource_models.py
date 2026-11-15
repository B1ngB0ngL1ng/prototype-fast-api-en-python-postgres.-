"""Reflection: bestaande PostgreSQL-tabellen zijn de bron van waarheid.
Er worden GEEN tabellen verwijderd of opnieuw aangemaakt bij serverstart.
"""
from sqlalchemy import MetaData, Table
from app.databases.connection import engine

RESOURCES = {
    "warehouses": "warehouses", "locations": "locations",
    "items": "items", "item_lines": "item_lines", "item_groups": "item_groups",
    "item_types": "item_types", "inventories": "inventories",
    "suppliers": "suppliers", "orders": "orders", "clients": "clients",
    "shipments": "shipments", "transfers": "transfers",
    "order_items": "order_items", "shipment_items": "shipment_items",
    "transfer_items": "transfer_items",
}
metadata = MetaData()
def table_for(resource):
    if resource not in RESOURCES:
        raise KeyError(resource)
    return Table(RESOURCES[resource], metadata, autoload_with=engine, extend_existing=True)
