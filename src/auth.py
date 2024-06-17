from datetime import datetime, timedelta, timezone
import logging
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.orm import Session

from database import get_db, models as db_model
from models import CurrentUser, TokenData
from config import get_settings

logging.getLogger('passlib').setLevel(logging.ERROR)

settings = get_settings()

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(
    data: TokenData, expires_delta: timedelta | None = None, db: Session | None = None
):
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    if db is not None:
        db_token = db_model.Token()
        db_token.token = encoded_jwt  # type: ignore
        db_token.uid = to_encode.get("uid")  # type: ignore
        db_token.expires = expire  # type: ignore
        db_token.ip = data.ip  # type: ignore
        db_token.user_agent = data.user_agent  # type: ignore
        db_token.desc = data.desc  # type: ignore
        db.add(db_token)
    return encoded_jwt


async def get_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    resp = HTTPException(status_code=401, detail="Invalid authentication credentials")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        uid = payload.get("uid")
        if uid is None:
            raise resp
        token_data = TokenData(**payload)
    except:
        raise resp
    db_token = (
        db.query(db_model.Token).filter(db_model.Token.token == token).one_or_none()
    )
    if db_token is None or token_data.uid != db_token.uid:
        raise resp
    return CurrentUser(user=db_token.user, token=token, token_data=token_data)


async def get_user_optional(
    db: Session = Depends(get_db), token=Depends(oauth2_scheme)
):
    try:
        return await get_user(db, token)
    except:
        return None
