from pydantic import BaseModel
from typing import Optional

class ItemSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None