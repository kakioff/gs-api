import json
from fastapi import Depends, Query, Request
from redis import Redis
import requests
from sqlmodel import Session, select, text
from auth import get_user
from database import get_db, get_user_redis
from database.models import Posts, Users
from models import CurrentUser
from utils import resp_succ
from . import router


@router.get("/dashboard")
async def root(
    req: Request,
    usr: CurrentUser = Depends(get_user),
    redis: Redis = Depends(get_user_redis),
    db: Session = Depends(get_db),
):
    post_count = db.exec(
        select(text("COUNT(*)")).select_from(Posts).where(Posts.uid == usr.user.uid)
    ).one()
    # 获取登陆历史
    history_res = redis.hgetall(usr.user.uid)
    history = []
    for k, v in history_res.items():  # type: ignore
        v_data = json.loads(v.decode("utf-8").replace("'", '"'))
        if v_data is None:
            continue
        history.append(
            {
                "time": v_data.get("time"),
                "device_id": v_data.get("device_id"),
                "ip": v_data.get("ip"),
                "user_agent": v_data.get("user_agent"),
                "desc": v_data.get("desc"),
            }
        )
    return resp_succ({"post_count": post_count, "history": history})


@router.get("/info-from-ip")
async def get_info_from_ip(req: Request, ip: str = Query(default=None)):
    if ip is None:
        ip = req.client.host
    res = requests.get(
        "https://opendata.baidu.com/api.php?query=219.139.196.108&co=&resource_id=6006&oe=utf8"
    )
    return resp_succ(res.json().get("data")[0])
