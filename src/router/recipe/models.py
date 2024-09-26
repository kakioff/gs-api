from typing import Any, Optional
from pydantic import BaseModel, Field


class CreateRecipe(BaseModel):
    name: str | None = None
    desc: str | None = None
    status: int | None = Field(None, ge=0, le=4)
    gid: int | None = None
    private: Optional[bool] = False


class CreateRecipeGroup(BaseModel):
    name: str | None = None
    desc: str | None = None
    status: int | None = Field(None, ge=0, le=2)
    private: Optional[bool] = False
    parent_id: Optional[int] = None


class CreateIngredient(BaseModel):
    name: str | None = None
    quantity: int | None = None
    unit: str | None = None
    desc: str | None = None

class CreateStep(BaseModel):
    title: str | None = None
    desc: str | None = None
    order: int | None = None