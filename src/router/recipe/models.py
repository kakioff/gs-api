from typing import Any, Optional
from pydantic import BaseModel


class CreateRecipe(BaseModel):
    name: str
    desc: str | None = None
    status: int | None = None
    group_id: int | None = None
    content: str | None = None
    cover: str | None = None
    materials: list[dict[str, Any]] | None = None
    private: Optional[bool] = False
