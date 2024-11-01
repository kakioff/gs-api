import logging
from fastapi import Depends, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from redis import Redis

from database import get_db, get_user_redis
from database.models import Users
from sqlmodel import Session
from database.mongodb_models import  User
from models import CurrentUser, create_token_data
from utils import encrypt_md5, resp_err, resp_succ
from .models import ChangeInfo, CreateUser, LoginRequest
from . import router
from beanie.operators import Or
from auth import create_access_token, get_user
from api import mail_server


@router.post("/login")
async def login(
    req: Request,
    usr: LoginRequest,
    device_id: str = Header(default=...),
    user_agent=Header(default=...),
    redis: Redis = Depends(get_user_redis),
):
    """
    登录接口
    """
    new_passwd = encrypt_md5(usr.passwd)
    user = await User.find_one(
        Or(User.name == usr.name, User.email == usr.name), User.hashed_password == new_passwd
    )
    # user = db.exec(
    #     select(Users).where(Users.name == usr.name, Users.hashed_password == new_passwd)
    # ).first()
    if user is None:
        return resp_err(detail="用户名或密码错误", code=401)
    token_data = create_token_data(
        user, req.client and req.client.host, user_agent, usr.desc or "登录", device_id
    )
    token = create_access_token(token_data, redis=redis)
    resp = user.to_resp()

    resp.update({"token": token})

    return resp_succ(data=resp, detail="登录成功")


@router.post("/token")
async def token(
    req: Request,
    device_id: str = Header(default="unknown"),
    user_agent=Header(default=...),
    usr: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_user_redis),
):
    """
    获取token接口，用于docs页面登录
    """
    new_passwd = encrypt_md5(usr.password)
    user = await User.find_one(
        User.name == usr.username, User.hashed_password == new_passwd
    )

    if user is None:
        return resp_err(detail="用户名或密码错误", code=401)
    token_data = create_token_data(
        user, req.client and req.client.host, user_agent, "/docs 登录", device_id
    )
    token = create_access_token(token_data, redis=redis)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/create")
async def create_user(usr: CreateUser):
    """
    创建用户接口
    """
    new_passwd = encrypt_md5(usr.passwd)
    new_user = User(
        name=usr.name,
        email=usr.email,
        phone=usr.phone,
        hashed_password=new_passwd,
        # id=new_uid
    )
    try:
        await User.insert(new_user)
    except Exception as e:
        logging.error(f"创建用户失败: {e}")
        new_user = None
    if new_user:
        return resp_succ(data=new_user.to_resp(), detail="创建成功")
    else:
        logging.error("创建用户失败")
        return resp_err(detail="创建失败", code=500)


@router.get("/info")
async def get_user_info(usr: CurrentUser = Depends(get_user)):
    """
    获取用户信息接口，需要登录才能访问
    """
    user = await User.get(usr.user.uid)
    # user = db.get(Users, usr.user.uid)
    if user is None:
        return resp_err(detail="用户不存在", code=404)
    return resp_succ(data=user.to_resp(), detail="获取信息成功")


@router.post("/check-password")
async def check_password(
    info: LoginRequest,
    usr: CurrentUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    """
    验证密码接口，需要登录才能访问
    """
    new_passwd = encrypt_md5(info.passwd)
    user = db.get(Users, usr.user.uid)
    if user is None:
        return resp_err(detail="用户不存在", code=404)

    if new_passwd == user.hashed_password:
        return resp_succ(detail="密码正确")
    return resp_err(detail="密码错误", code=401)


@router.get("/logout")
async def logout(
    usr: CurrentUser = Depends(get_user), redis: Redis = Depends(get_user_redis)
):
    """
    登出接口，需要登录才能访问，删除用户的token信息，实现登出功能。
    """
    # token = db.exec(select(Tokens).where(Tokens.token == usr.token)).one_or_none()
    # if token is not None:
    # db.delete(token)
    # db.commit()
    redis.hdel(usr.user.uid, usr.token)
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
    user = db.get(Users, usr.user.uid)
    if user is None:
        return resp_err(detail="用户不存在", code=404)

    if opts.uname is not None and opts.uname != user.name:
        user.name = opts.uname
    if opts.email is not None and opts.email != user.email:
        user.email = opts.email
    if opts.phone is not None and opts.phone != user.phone:
        user.phone = opts.phone
    if opts.passwd is not None:
        new_passwd = encrypt_md5(opts.passwd)
        user.hashed_password = new_passwd
    db.add(user)
    db.commit()
    db.refresh(user)
    return resp_succ(data=user.to_resp(), detail="更新成功")
