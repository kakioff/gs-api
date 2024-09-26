""" 
需要管理员权限的接口
"""

from sqlmodel import Session, select
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from auth import get_user_admin
from database import get_db
from database.models import Users
from models import CurrentUser
from router.user.models import AdminChangeInfo
from utils import encrypt_md5, resp_err, resp_succ


from . import router as f_router


router = APIRouter(prefix="/admin", tags=["Admin", "User"])


@router.get("/all-users")
def get_all_users(
    size: int = Query(default=20),
    page: int = Query(default=1),
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user_admin),
):
    """
    获取所有用户信息，需要管理员权限
    """
    user = usr.user
    if user.role_id <= 3:
        return resp_err(detail="权限不足", code=403)
    all_count = db.exec(
        select(func.count()).select_from(Users).where(Users.role_id < user.role_id)
    ).one()

    all_users = db.exec(
        select(Users)
        .where(Users.role_id < user.role_id)
        .offset(size * (page - 1))
        .limit(size)
    ).all()
    return resp_succ([u.to_resp() for u in all_users], total=all_count)


@router.post("/update/{user_id}")
def update_user(
    user_id: int,
    opts: AdminChangeInfo,
    usr: CurrentUser = Depends(get_user_admin),
    db: Session = Depends(get_db),
):
    """更新用户信息"""
    if opts.role_id is not None and opts.role_id >= usr.user.role_id:
        # 不能修改权限大于等于自己的用户权限
        return resp_err(detail="权限不足", code=403)
    user = db.exec(
        select(Users).where(Users.id == user_id, Users.role_id < usr.user.role_id)
    ).one_or_none()
    if user is None:
        return resp_err(detail="用户不存在", code=404)
    if opts.role_id is not None:
        user.role_id = opts.role_id
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
    return resp_succ(user.to_resp(), detail="更新成功")


@router.delete("/delete/{user_id}")
def delete_user(
    user_id: int,
    usr: CurrentUser = Depends(get_user_admin),
    db: Session = Depends(get_db),
):
    """删除用户"""
    user = db.exec(
        select(Users).where(Users.id == user_id, Users.role_id < usr.user.role_id)
    ).one_or_none()
    if user is None:
        return resp_err(detail="用户不存在", code=404)
    db.delete(user)
    db.commit()
    return resp_succ(detail="删除成功")


f_router.include_router(router)
