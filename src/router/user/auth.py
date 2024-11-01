""" 
需要管理员权限的接口
"""

import logging
import os
from redis import Redis
import requests
from fastapi import APIRouter, Depends, Header, Query, Request
from api import click_up, cos, github
from auth import create_access_token, get_user
from config import Settings, get_settings
from database import get_user_redis
from database.mongodb_models import DBFile, GithubInfo, User
from models import CurrentUser, create_token_data
from utils import resp_err, resp_succ
from beanie.operators import Or

from . import router as f_router


router = APIRouter(prefix="/auth", tags=["Auth", "User"])


def get_user_with_token(req: Request, user: User, user_agent: str, redis: Redis, provider: str):
    token_data = create_token_data(
        user, req.client and req.client.host, user_agent, f"{provider} 登录", f"{provider}--"
    )
    token = create_access_token(token_data, redis=redis)
    resp = user.to_resp()
    resp.update({"token": token})
    return resp


def update_github_user(user: User, github_info: dict):
    """
    更新用户信息

    :param user: 用户信息
    :param github_info: Github用户信息
    :return: user, changed
    :rtype: tuple
    """
    github_id = github_info.get("id")
    github_name = github_info.get("name")
    github_email = github_info.get("email")
    changed = False
    if user.github.id != github_id:
        user.github.id = github_id
        changed = True
    if user.github.name != github_name:
        user.github.name = github_name
        changed = True
    if user.email is None and github_email:
        user.email = github_email
        changed = True
    if user.github.email != github_email:
        user.github.email = github_email
        changed = True
    return user, changed


@router.get("/login-with-github")
async def login_with_github(
    req: Request,
    user_agent: str = Header(...),
    token: str = Query(...),
    settings: Settings = Depends(get_settings),
    redis: Redis = Depends(get_user_redis),
):
    try:
        github_info = github.get_user(token)
        assert github_info is not None
    except:
        return resp_err(detail="Github Token Error", code=401)
    github_id = github_info["id"]
    github_name = github_info["name"]
    github_email = github_info["email"]

    user = await User.find_one(
        Or(
            User.github.id == github_id,
            User.github.email == github_email,
            User.email == github_email,
        ),
    )

    if user is None:
        user = User(
            name=github_name,
            email=github_email,
            phone=github_info.get("phone"),
            github=GithubInfo(
                id=github_id,
                email=github_email,
                name=github_name,
            ),
        )
        try:
            await user.save()
        except Exception as e:
            logging.error(f"创建用户失败: {e}")
            return resp_err(detail="登录失败", code=500)

    user, changed = update_github_user(user, github_info)

    if user.avatar_id is None:
        img_res = requests.get(github_info["avatar_url"])
        if img_res.status_code == 200:
            temp_img_path = f"{settings.temp_dir}/{github_info['id']}.png"
            cloud_path = f"/users/{user.id}/avatar/{github_info['id']}.png"
            with open(temp_img_path, "wb") as f:
                f.write(img_res.content)

            res = cos.upload_file(temp_img_path, cloud_path)
            file_db = DBFile(
                name=f"github_{github_id}",
                hidden=True,
                size=os.path.getsize(temp_img_path),
                path=cloud_path,
                type="png",
                uid=str(user.id),
                etag=res["ETag"],
            )
            await file_db.save()
            os.remove(temp_img_path)
            user.avatar_id = str(file_db.id)
            changed = True
    if changed:
        await user.save()
    resp = get_user_with_token(
        req, user, user_agent, redis, "github"
    )
    return resp_succ(data=resp)


@router.get("/link-github")
async def link_github(
    req: Request,
    user_agent: str = Header(...),
    token: str = Query(...),
    redis: Redis = Depends(get_user_redis),
    usr: CurrentUser = Depends(get_user),
):
    user = await User.get(usr.user.uid)
    if user is None:
        return resp_err(detail="用户不存在", code=404)
    github_info = github.get_user(token)
    user, changed = update_github_user(user, github_info)
    if changed:
        await user.save()
    resp = get_user_with_token(
        req, user, user_agent, redis, "github"
    )
    return resp_succ(data=resp)


@router.get("/login-with-click-up")
async def login_with_click_up(
    req: Request,
    user_agent: str = Header(...),
    token: str = Query(...),
    redis: Redis = Depends(get_user_redis),
):
    try:
        clickup_info = click_up.get_user(token)
        assert clickup_info is not None
    except:
        return resp_err(detail="ClickUp Token Error", code=401)
    clickup_id = clickup_info["id"]
    clickup_name = clickup_info["username"]
    clickup_email = clickup_info["email"]
    user = await User.find_one(
        Or(
            User.clickup.id == clickup_id,
            User.clickup.email == clickup_email,
            User.email == clickup_email,
        )
    )

    if user is None:
        user = User(
            name=clickup_name,
            email=clickup_email,
            phone=clickup_info.get("phone"),
        )
        try:
            await user.save()
        except Exception as e:
            logging.error(f"创建用户失败: {e}")
            return resp_err(detail="登录失败", code=500)
    
    user, changed = update_clickup_user(user, clickup_info)

    if changed:
        await user.save()

    resp = get_user_with_token(
        req, user, user_agent, redis, "click-up"
    )
    return resp_succ(data=resp)

def update_clickup_user(user: User, clickup_info: dict):
    clickup_id = clickup_info.get("id")
    clickup_name = clickup_info.get("username")
    clickup_email = clickup_info.get("email")
    
    changed = False
    if user.clickup.id != clickup_id:
        user.clickup.id = clickup_id
        changed = True
    if user.clickup.name != clickup_name:
        user.clickup.name = clickup_name
        changed = True
    if user.email is None and clickup_email:
        user.email = clickup_email
        changed = True
    if user.clickup.email != clickup_email:
        user.clickup.email = clickup_email
        changed = True
    return user, changed

@router.get("/link-click-up")
async def link_click_up(
    req: Request,
    user_agent: str = Header(...),
    token: str = Query(...),
    redis: Redis = Depends(get_user_redis),
    usr: CurrentUser = Depends(get_user),
):
    user = await User.get(usr.user.uid)
    if user is None:
        return resp_err(detail="用户不存在", code=404)
    clickup_info = click_up.get_user(token)
    user, changed = update_clickup_user(user, clickup_info)
    if changed:
        await user.save()
    resp = get_user_with_token(
        req, user, user_agent, redis, "click-up"
    )
    return resp_succ(data=resp)


f_router.include_router(router)
