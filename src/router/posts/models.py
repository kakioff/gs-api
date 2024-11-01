from datetime import datetime
from pydantic import BaseModel


class CreatePost(BaseModel):
    """Create post model"""

    title: str = "还没有标题"
    content: str = ""
    created: datetime | None = None
    status: int = 0
    private: bool = False


class UpdatePost(BaseModel):
    """Update post model"""

    title: str | None = None
    content: str | None = None
    status: int | None = None
    private: bool | None = None
