"""Importeer vier CargoHub JSON-bestanden in bestaande PostgreSQL-tabellen.

Plaats dit bestand in app/scripts/import_cargohub.py.
Start vanuit de projecthoofdmap met:
    python -m app.scripts.import_cargohub
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from app.databases.connection import engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).resolve().parent
FILES = (
    ("warehouses", ("warehouses.json", "warehouse.json")),
    ("locations", ("location.json", "locations.json")),
    ("orders", ("order.json", "orders.json")),
    ("order_items", ("order_item.json", "order_items.json")),
)


def load_records(names):
    path = next((DATA_DIR / name for name in names if (DATA_DIR / name).is_file()), None)
    if path is None:
        raise FileNotFoundError(f"Geen bestand gevonden voor {names} in {DATA_DIR}")
    with path.open(encoding="utf-8-sig") as file:
        records = json.load(file)
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError(f"{path.name} moet een JSON-lijst met objecten bevatten")
    print(f"{path.name}: {len(records)} records gelezen")
    return records


def newest_record(records):
    return max(records, key=lambda r: datetime.fromisoformat(
        (r.get("updated_at") or r.get("created_at") or "1970-01-01T00:00:00Z").replace("Z", "+00:00")
    ))


def deduplicate(table, records):
    by_id = {}
    for record in records:
        if "id" not in record:
            raise ValueError(f"{table}: record zonder id: {record}")
        by_id.setdefault(record["id"], []).append(record)
    duplicate_ids = [record_id for record_id, versions in by_id.items() if len(versions) > 1]
    if duplicate_ids:
        print(f"{table}: dubbele IDs {duplicate_ids}; nieuwste updated_at behouden")
    return [newest_record(versions) for versions in by_id.values()]


def validate_relations(data):
    warehouse_ids = {r["id"] for r in data["warehouses"]}
    order_ids = {r["id"] for r in data["orders"]}
    for table in ("locations", "orders"):
        missing = {r["warehouse_id"] for r in data[table]} - warehouse_ids
        if missing:
            raise ValueError(f"{table}: ontbrekende warehouse IDs: {sorted(missing)}")
    missing_orders = {r["order_id"] for r in data["order_items"]} - order_ids
    if missing_orders:
        raise ValueError(f"order_items: ontbrekende order IDs: {sorted(missing_orders)[:20]}")


def import_data():
    print(f"Data-map: {DATA_DIR}")
    data = {table: deduplicate(table, load_records(names)) for table, names in FILES}
    validate_relations(data)

    # Niets wijzigen als de tabellen al gegevens bevatten.
    with engine.begin() as connection:
        for table, _ in FILES:
            count = connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            if count:
                raise RuntimeError(
                    f"Tabel '{table}' bevat al {count} records. "
                    "Import afgebroken om bestaande gegevens te beschermen."
                )

        for table, _ in FILES:
            records = data[table]
            if not records:
                print(f"{table}: leeg, overgeslagen")
                continue
            # Neem alle JSON-velden mee; optionele velden krijgen None.
            columns = list(dict.fromkeys(key for record in records for key in record))
            params = [{column: record.get(column) for column in columns} for record in records]
            columns_sql = ", ".join(f'"{column}"' for column in columns)
            placeholders = ", ".join(f":{column}" for column in columns)
            connection.execute(
                text(f"INSERT INTO {table} ({columns_sql}) VALUES ({placeholders})"),
                params,
            )
            # Synchroniseer de PostgreSQL identity sequence met de ingevoerde IDs.
            connection.execute(
                text("SELECT setval(pg_get_serial_sequence(:table, 'id'), :max_id, true)"),
                {"table": table, "max_id": max(r["id"] for r in records)},
            )
            print(f"{table}: {len(records)} records ingevoegd")

    print("\nKlaar! Alle imports zijn opgeslagen.")


if __name__ == "__main__":
    import_data()
