from pydantic import BaseModel


class LoginRequest(BaseModel):
    name: str
    passwd: str
    desc: str | None = None


class CreateUser(BaseModel):
    name: str
    passwd: str
    email: str | None = None
    phone: str | None = None

class ChangeInfo(BaseModel):
    uname: str | None = None
    email: str | None = None
    phone: str | None = None
    passwd: str | None = None

class AdminChangeInfo(ChangeInfo):
    role_id: int | None = None