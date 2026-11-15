
import json
from pathlib import Path

from sqlalchemy import text
from app.databases.connection import engine


# Hoofdmap van het project
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


# Volgorde is belangrijk vanwege foreign keys
TABLES = [
    ("warehouses", "warehouse.json"),
    ("locations", "location.json"),
    ("orders", "order.json"),
    ("order_items", "order_item.json"),
]


def load_json(filename):
    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def import_data():
    # Lees eerst alle bestanden in.
    datasets = {}

    for table, filename in TABLES:
        records = load_json(filename)

        # Bij de originele orders ontbreekt soms created_at.
        if table == "orders":
            for record in records:
                record.setdefault("created_at", None)

        datasets[table] = records

    # Alle imports gebeuren in één transactie.
    with engine.begin() as connection:

        # Voorkom dat we bestaande data overschrijven.
        for table, _ in TABLES:
            count = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            ).scalar_one()

            if count != 0:
                raise ValueError(
                    f"Tabel {table} bevat al {count} records. "
                    "Import gestopt."
                )

        for table, _ in TABLES:
            records = datasets[table]

            if not records:
                continue

            columns = list(records[0].keys())

            column_names = ", ".join(columns)
            parameters = ", ".join(
                f":{column}" for column in columns
            )

            query = text(
                f"INSERT INTO {table} ({column_names}) "
                f"VALUES ({parameters})"
            )

            connection.execute(query, records)

            # Werk de ID-teller bij.
            connection.execute(
                text(f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table}', 'id'),
                        (SELECT MAX(id) FROM {table}),
                        true
                    )
                """)
            )

            print(
                f"{table}: {len(records)} records geïmporteerd"
            )

    print("Import succesvol afgerond!")


if __name__ == "__main__":
    import_data()
