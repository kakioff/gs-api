from typing import Type, TypeVar
from pydantic import BaseModel

from database.models import User

T = TypeVar('T', bound=BaseModel)

def to_pydantic(db_object, pydantic_model: Type[T]) -> T:
    return pydantic_model(**db_object.__dict__)


# class Token(BaseModel):
#     access_token: str
#     token_type: str


# class User(BaseModel):
#     uname: str


class TokenData(BaseModel):
    uid: int
    ip: str | None = None
    user_agent: str | None = None
    desc: str | None = None

class CurrentUser(BaseModel):
    user: User
    token: str
    token_data: TokenData
    
    class Config:
        arbitrary_types_allowed = True