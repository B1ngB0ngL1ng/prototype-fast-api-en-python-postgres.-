from sqlalchemy import select, insert, update, delete, and_
from sqlalchemy.exc import IntegrityError, DataError
from fastapi import HTTPException
from app.models.resource_models import table_for

class ResourceRepository:
    def __init__(self, db, resource):
        self.db = db
        self.resource = resource
        try:
            self.table = table_for(resource)
        except Exception as exc:
            raise HTTPException(503, f"Tabel {resource} ontbreekt. Voer eerst bootstrap uit.") from exc

    def _key(self):
        pk = list(self.table.primary_key.columns)
        if not pk:
            raise HTTPException(500, f"Tabel {self.resource} heeft geen primary key")
        return pk

    def _where_id(self, identifier):
        pk = self._key()
        if len(pk) != 1:
            raise HTTPException(400, "Deze resource gebruikt een samengestelde sleutel; gebruik de speciale inventory-route.")
        return pk[0] == identifier

    def _dict(self, row):
        return dict(row._mapping)

    def list(self, limit=100, offset=0, field=None, value=None):
        stmt = select(self.table)
        if field is not None:
            if field not in self.table.c:
                raise HTTPException(400, f"Onbekend veld: {field}")
            stmt = stmt.where(self.table.c[field] == value)
        return [self._dict(x) for x in self.db.execute(stmt.limit(limit).offset(offset)).all()]

    def get(self, identifier):
        row = self.db.execute(select(self.table).where(self._where_id(identifier))).first()
        if row is None:
            raise HTTPException(404, f"{self.resource} met ID {identifier} niet gevonden")
        return self._dict(row)

    def validate(self, payload):
        if not isinstance(payload, dict):
            raise HTTPException(422, "JSON-object verwacht")
        unknown = set(payload) - set(self.table.c.keys())
        if unknown:
            raise HTTPException(422, f"Onbekende velden: {sorted(unknown)}")
        return payload

    def _commit(self):
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409, "Databaseconflict: unieke sleutel of relatie ongeldig") from exc
        except DataError as exc:
            self.db.rollback()
            raise HTTPException(422, "Ongeldig datatype voor databasekolom") from exc

    def create(self, payload):
        payload = self.validate(payload)
        try:
            row = self.db.execute(insert(self.table).values(**payload).returning(*self.table.c)).first()
            self._commit()
            return self._dict(row)
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409, "Databaseconflict: ongeldige relatie of dubbele sleutel") from exc
        except DataError as exc:
            self.db.rollback()
            raise HTTPException(422, "Ongeldige databasewaarde") from exc

    def update(self, identifier, payload):
        self.get(identifier)
        payload = self.validate(payload)
        for col in self._key():
            payload.pop(col.name, None)
        if not payload:
            return self.get(identifier)
        try:
            self.db.execute(update(self.table).where(self._where_id(identifier)).values(**payload))
            self._commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409, "Databaseconflict: ongeldige relatie of dubbele sleutel") from exc
        except DataError as exc:
            self.db.rollback()
            raise HTTPException(422, "Ongeldige databasewaarde") from exc
        return self.get(identifier)

    def delete(self, identifier):
        self.get(identifier)
        try:
            self.db.execute(delete(self.table).where(self._where_id(identifier)))
            self._commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409, "Databaseconflict: ongeldige relatie of dubbele sleutel") from exc
        except DataError as exc:
            self.db.rollback()
            raise HTTPException(422, "Ongeldige databasewaarde") from exc
