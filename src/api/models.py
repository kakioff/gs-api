from datetime import datetime
from pydantic import BaseModel


class CosOwner(BaseModel):
    ID: str
    DisplayName: str


class CosFileItem(BaseModel):
    Key: str
    LastModified: datetime
    ETag: str
    Size: int
    Owner: CosOwner
    StorageClass: str
    isFile: bool=False
