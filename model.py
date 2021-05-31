from typing import Optional
from pydantic import BaseModel

class Bug(BaseModel):
    id: int
    name: str
    date: str
    from_user: str
    comment: Optional[str] = None

