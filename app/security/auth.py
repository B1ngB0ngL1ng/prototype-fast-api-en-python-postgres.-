import json
import os
from pathlib import Path
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="API_KEY", auto_error=False)
USER_FILE = Path(__file__).resolve().parents[2] / "data" / "user.json"

def require_permission(resource, method):
    def dependency(key: str | None = Security(api_key_header)):
        if os.getenv("CARGOHUB_REQUIRE_API_KEY", "true").lower() != "true":
            return {"app": "development"}
        if not key:
            raise HTTPException(401, "API_KEY ontbreekt")
        users = json.loads(USER_FILE.read_text(encoding="utf-8"))
        user = next((x for x in users if x.get("api_key") == key), None)
        if user is None:
            raise HTTPException(401, "Ongeldige API_KEY")
        if not user.get("endpoint_access", {}).get(resource, {}).get(method.lower(), False):
            raise HTTPException(403, f"Geen {method.upper()} toegang tot {resource}")
        return user
    return dependency
