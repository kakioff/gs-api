from datetime import datetime, timedelta, timezone
import json
import logging
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from redis import Redis
from sqlmodel import Session

from database import get_user_redis
from models import CurrentUser, TokenData
from config import get_settings

logging.getLogger("passlib").setLevel(logging.ERROR)

settings = get_settings()

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/token", auto_error=True, scopes={
    "me": "获取用户信息",
    "admin": "管理员权限",
})


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(
    data: TokenData,
    expires_delta: timedelta | None = None,
    redis: Redis | None = None,
):
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    # if db is not None:
    #     db_token = db_model.Tokens(
    #         token=encoded_jwt,
    #         uid=to_encode.get("uid", 0),
    #         expires=expire,
    #         ip=data.ip,
    #         user_agent=data.user_agent,
    #         desc=data.desc,
    #     )
    #     db.add(db_token)
    #     db.commit()
    if redis:
        redis.hset(
            data.uid,
            encoded_jwt,
            json.dumps(
                {
                    "time": datetime.now(timezone.utc).timestamp(),
                    **data.model_dump()
                }
            ),
        )
        redis.hexpireat(data.uid, expire, encoded_jwt)
    return encoded_jwt


async def get_user(
    req: Request,
    redis: Redis = Depends(get_user_redis),
    token: str = Depends(oauth2_scheme),
):
    resp = HTTPException(status_code=401, detail="用户认证失败")
    try:
        if type(token) is not str:
            token = await oauth2_scheme(req)  # type: ignore

        assert token, "用户认证失败"
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        uid = payload.get("uid")
        if uid is None:
            raise resp
        token_data = TokenData(**payload)
    except Exception as e:
        raise resp
    # db_token = db.exec(
    #     select(db_model.Tokens).where(db_model.Tokens.token == token)
    # ).one_or_none()
    if redis.hget(uid, token) is None:  # or token_data.uid != db_token.uid:
        raise resp
    return CurrentUser(user=token_data, token=token)
    # return CurrentUser(user=db_token.user, token=token, token_data=token_data)


async def get_user_optional(req: Request, redis: Redis = Depends(get_user_redis)):
    try:
        usr = await get_user(req, redis)
        return usr
    except Exception as e:
        logging.error(e)
        return None


async def get_user_admin(req: Request, redis: Redis = Depends(get_user_redis)):
    usr = await get_user(req, redis)
    if usr.user.role_name in ["admin", "super"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return usr

async def get_user_super(req: Request, redis: Redis = Depends(get_user_redis)):
    usr = await get_user(req, redis)
    if usr.user.role_name == "super":
        raise HTTPException(status_code=403, detail="Permission denied")
    return usr
