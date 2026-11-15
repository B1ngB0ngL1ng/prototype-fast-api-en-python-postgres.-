"""Maak ALLEEN ontbrekende tabellen aan; bestaande tabellen en rijen blijven intact.
Kolommen van ontbrekende tabellen worden uit meegeleverde JSON afgeleid.
Dit is een prototype-bootstrap, geen productie-databasemigratie.
"""
import json
from pathlib import Path
from sqlalchemy import MetaData, Table, Column, Integer, Float, Boolean, Text, DateTime, inspect
from sqlalchemy import PrimaryKeyConstraint
from app.databases.connection import engine

FILES = {
    "warehouses": "warehouse.json", "locations": "location.json",
    "items": "item.json", "item_lines": "item_line.json",
    "item_groups": "item_group.json", "item_types": "item_type.json",
    "inventories": "inventory.json", "suppliers": "supplier.json",
    "orders": "order.json", "clients": "client.json",
    "shipments": "shipment.json", "transfers": "transfer.json",
    "order_items": "order_item.json", "shipment_items": "shipment_item.json",
    "transfer_items": "transfer_item.json",
}
DATA = Path(__file__).resolve().parents[2] / "data"

def guess_type(key, values):
    present = [v for v in values if v is not None]
    if key.endswith("_at") or key.endswith("_date"):
        return DateTime(timezone=True)
    if present and all(isinstance(v, bool) for v in present):
        return Boolean()
    if present and all(isinstance(v, int) and not isinstance(v, bool) for v in present):
        return Integer()
    if present and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in present):
        return Float()
    return Text()

def main():
    existing = set(inspect(engine).get_table_names())
    meta = MetaData()
    for table, filename in FILES.items():
        if table in existing:
            print(f"Behoud bestaande tabel: {table}")
            continue
        path = DATA / filename
        records = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        fields = {k for row in records for k in row}
        if table == "clients" and not fields:
            fields = {"id", "name", "address", "city", "zip_code", "province",
                      "country", "contact_name", "contact_phone", "contact_email"}
        cols = [Column(k, guess_type(k, [r.get(k) for r in records]),
                       primary_key=(k == "id")) for k in sorted(fields)]
        if table == "inventories":
            cols = [Column(k, guess_type(k, [r.get(k) for r in records]))
                    for k in sorted(fields)]
            Table(table, meta, *cols, PrimaryKeyConstraint("item_id", "location_id"))
        else:
            Table(table, meta, *cols)
        print(f"Nieuwe tabel gepland: {table}")
    meta.create_all(engine, checkfirst=True)
    print("Bootstrap voltooid. Bestaande records zijn niet verwijderd.")

if __name__ == "__main__":
    main()
