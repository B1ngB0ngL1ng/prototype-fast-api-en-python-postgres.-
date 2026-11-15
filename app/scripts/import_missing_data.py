"""Importeer uitsluitend in LEGE tabellen; bestaande gegevens worden nooit overschreven."""
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import MetaData, Table, select, func
from app.databases.connection import engine
from app.scripts.bootstrap_database import FILES, DATA

def normalize(row, columns):
    out = {}
    for key, value in row.items():
        if key not in columns:
            continue
        col = columns[key]
        if isinstance(value, str) and isinstance(col.type, __import__("sqlalchemy").DateTime):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        out[key] = value
    return out

def main():
    for name, filename in FILES.items():
        path = DATA / filename
        if not path.exists():
            print(f"Geen bronbestand voor {name}: overgeslagen")
            continue
        records = json.loads(path.read_text(encoding="utf-8"))
        table = Table(name, MetaData(), autoload_with=engine)
        with engine.begin() as conn:
            count = conn.execute(select(func.count()).select_from(table)).scalar_one()
            if count:
                print(f"{name}: al {count} records, overgeslagen")
                continue
            keys = ("item_id", "location_id") if name == "inventories" else ("id",)
            deduped = {}
            for row in records:
                identity = tuple(row.get(k) for k in keys)
                if all(v is not None for v in identity):
                    deduped[identity] = row
            rows = [normalize(x, table.c) for x in deduped.values()]
            for start in range(0, len(rows), 500):
                conn.execute(table.insert(), rows[start:start+500])
            print(f"{name}: {len(rows)} geïmporteerd")
    print("Import voltooid")

if __name__ == "__main__":
    main()
