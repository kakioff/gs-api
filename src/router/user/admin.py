""" 
需要管理员权限的接口
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from auth import get_user
from database import get_db
from database.models import User
from models import CurrentUser
from utils import resp_err


from . import router as f_router


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/all-users")
async def get_all_users(
    db: Session = Depends(get_db), usr: CurrentUser = Depends(get_user)
):
    user: User = usr.user
    if user.role_id <= 3:
        return resp_err(detail="权限不足", code=403)
    # 获取所有用户信息，需要管理员权限
    return {"message": "Get all users"}


f_router.include_router(router)
