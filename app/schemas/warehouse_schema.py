
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WarehouseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    address: str
    city: str
    zip_code: str
    province: str
    country: str
    contact_name: str
    contact_phone: str
    contact_email: str
    created_at: datetime
    updated_at: datetime
