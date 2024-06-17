from fastapi import Depends, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from database.models import Token, User
from sqlalchemy.orm import Session

from models import TokenData, CurrentUser
from utils import encrypt_md5, resp_err, resp_succ
from .models import ChangeInfo, CreateUser, LoginRequest
from . import router
from auth import create_access_token, get_password_hash, get_user


@router.post("/login")
async def login(
    req: Request,
    usr: LoginRequest,
    user_agent=Header(default=...),
    db: Session = Depends(get_db),
):
    """
    登录接口
    """
    new_passwd = encrypt_md5(usr.passwd)
    user = (
        db.query(User)
        .filter(User.name == usr.name, User.hashed_password == new_passwd)
        .one_or_none()
    )
    if user is None:
        return resp_err(detail="用户名或密码错误", code=401)
    token_data = TokenData(
        uid=user.id,  # type: ignore
        ip=req.client and req.client.host,
        user_agent=user_agent,
        desc=usr.desc or "登录",
    )
    token = create_access_token(token_data, db=db)
    resp = user.to_resp()
    resp.update({"token": token})
    return resp_succ(data=resp, detail="登录成功")


@router.post("/token")
async def token(
    req: Request,
    user_agent=Header(default=...),
    usr: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    获取token接口，用于docs页面登录
    """
    new_passwd = encrypt_md5(usr.password)
    user = (
        db.query(User)
        .filter(User.name == usr.username, User.hashed_password == new_passwd)
        .one_or_none()
    )
    if user is None:
        return resp_err(detail="用户名或密码错误", code=401)
    token_data = TokenData(
        uid=user.id,  # type: ignore
        ip=req.client and req.client.host,
        user_agent=user_agent,
        desc="docs 登录",
    )
    token = create_access_token(token_data, db=db)
    return {"access_token": token, "token_type": "bearer"}


@router.put("/create")
async def create_user(usr: CreateUser, db: Session = Depends(get_db)):
    """
    创建用户接口
    """
    new_passwd = encrypt_md5(usr.passwd)
    new_user = User()
    new_user.name = usr.name  # type: ignore
    new_user.hashed_password = new_passwd  # type: ignore
    new_user.email = usr.email  # type: ignore
    new_user.phone = usr.phone  # type: ignore
    new_user.role_id = 3  # type: ignore
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return resp_succ(data=new_user.to_resp(), detail="创建成功")


@router.get("/info")
async def get_user_info(usr: CurrentUser = Depends(get_user)):
    """
    获取用户信息接口，需要登录才能访问
    """
    user: User = usr.user
    return resp_succ(data=user.to_resp(), detail="获取信息成功")


@router.get("/logout")
async def logout(usr: CurrentUser = Depends(get_user), db: Session = Depends(get_db)):
    """
    登出接口，需要登录才能访问，删除用户的token信息，实现登出功能。
    """
    db.query(Token).filter(Token.token == usr.token).delete()
    return resp_succ(detail="登出成功")


@router.post("/update")
async def update_user(
    opts: ChangeInfo,
    usr: CurrentUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    """
    更新用户信息接口，需要登录才能访问。
    """
    user: User = usr.user
    if opts.uname is not None and opts.uname != user.name:
        user.name = opts.uname  # type: ignore
    if opts.email is not None and opts.email != user.email:
        user.email = opts.email  # type: ignore
    if opts.phone is not None and opts.phone != user.phone:
        user.phone = opts.phone  # type: ignore
    if opts.passwd is not None:
        new_passwd = encrypt_md5(opts.passwd)
        user.hashed_password = new_passwd  # type: ignore
    db.commit()
    db.refresh(user)
    return resp_succ(data=user.to_resp(), detail="更新成功")
