import datetime
from typing import Optional
from beanie import Document
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field


class Role(BaseModel):
    # id: int
    label: str
    name: str


class GithubInfo(BaseModel):
    id: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)

class ClickUpInfo(BaseModel):
    id: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)

class User(Document):
    # id: str
    name: str
    email: Optional[EmailStr] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    hashed_password: Optional[str] = Field(default=None)
    role: Role = Field(default=Role(label="普通用户", name="user"))

    # github
    github: GithubInfo = Field(default=GithubInfo())
    clickup: ClickUpInfo = Field(default=ClickUpInfo())

    avatar_id: Optional[str] = Field(default=None)
    # avatar: Optional["Files"] = Relationship(back_populates="user_avatar")

    class Settings:
        name = "users"

    def to_resp(self):
        uid = str(self.id)
        return {
            "id": uid,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role.model_dump(),
            "has_password": bool(self.hashed_password),
            "avatar": f"/file/avatar/{uid}",  # if self.avatar_id else None,
            "github": self.github.model_dump() if self.github.id else None,
            "click-up": self.clickup.model_dump() if self.clickup.id else None,
        }


class DBFile(Document):

    name: Optional[str] = None
    size: int
    path: str
    type: str
    etag: Optional[str] = None
    created: datetime.datetime = Field(default=datetime.datetime.now())
    updated: Optional[datetime.datetime] = Field(default=None)
    uid: str = Field(ObjectId)

    hidden: bool = False

    class Settings:
        name = "files"

    def get_user(self):
        return User.get(self.uid)


models = [User, DBFile]
