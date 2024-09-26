from datetime import datetime
from pydantic import BaseModel


class CreatePost(BaseModel):
    """Create post model"""

    title: str = "还没有标题"
    content: str = ""
    created: datetime = datetime.now()
    status: int = 0
    private: bool = False