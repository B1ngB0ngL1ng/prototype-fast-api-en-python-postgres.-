from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class ResourceInput(BaseModel):
    model_config = ConfigDict(extra="allow")
    # Alle overige velden worden gecontroleerd tegen de echte DB-kolommen.
    # Voor productie kun je per resource strengere Pydantic-schemas toevoegen.
    pass

class ItemListInput(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
