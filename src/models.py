from typing import Type, TypeVar
from pydantic import BaseModel

from database.mongodb_models import User

T = TypeVar("T", bound=BaseModel)

# class Token(BaseModel):
#     access_token: str
#     token_type: str


# class User(BaseModel):
#     uname: str


class TokenData(BaseModel):
    uid: str
    uname: str | None = None
    role_name: str
    device_id: str
    ip: str | None = None
    user_agent: str | None = None
    desc: str | None = None

def create_token_data(user: User, ip, user_agent, desc, device_id: str = "unknown"):
    return TokenData(
        uid=str(user.id),
        uname=user.name,
        role_name=user.role.name,
        device_id=device_id,
        ip=ip,
        user_agent=user_agent,
        desc=desc or "登录",
    )


class CurrentUser(BaseModel):
    user: TokenData
    token: str
    # token_data: TokenData

    # class Config:
    #     arbitrary_types_allowed = True
