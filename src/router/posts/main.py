import datetime
from typing import Optional
from fastapi import Depends, Query
from sqlmodel import Session, select, text
from auth import get_user, get_user_optional
from database import get_db
from database.models import Posts
from models import CurrentUser
from router.posts.models import CreatePost, UpdatePost
from utils import resp_err, resp_succ
import utils
from . import router


@router.get("/all")
def all_posts(
    page: int = Query(1),
    limit: int = Query(10),
    mine: bool = Query(False),
    search: str = Query(None),
    sort: str = Query("created desc"),
    db: Session = Depends(get_db),
    console: bool = Query(False),
    usr: Optional[CurrentUser] = Depends(get_user_optional),
):
    """Get all posts"""
    page = page - 1
    sql_where = []

    # sql = select(Posts)
    if not console:
        sql_where.append("status = 1")
        private_str = "private = 0"
        if usr:
            private_str += f" or uid = '{usr.user.uid}'"
        sql_where.append(private_str)
    elif usr:
        sql_where.append(f"uid = '{usr.user.uid}'")

    if search:
        sql_where.append(f"title like '%{search}%' or content like '%{search}%'")
    if mine and usr:
        sql_where.append(f"uid = '{usr.user.uid}'")
    
    sql_where = f"({') and ('.join(sql_where)})" if sql_where else ""
    
    count = db.execute(
        text(f"select count(*) from posts {'where' if sql_where else ''} {sql_where}")
    ).scalar()
    sql = (
        select(Posts)
        .where(text(sql_where))
        .offset(page * limit)
        .limit(limit)
    )
    if sort:
        sql = sql.order_by(text(sort))
    posts = db.exec(sql).all()

    return resp_succ([post.to_resp() for post in posts], total=count)


@router.put("/create")
def create_post(
    new_post_conf: CreatePost,
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user),
):
    """Create a post"""
    if new_post_conf.created is None:
        new_post_conf.created = datetime.datetime.now()
    post_id = utils.generate_uid("post")
    new_post = Posts(**new_post_conf.dict(), id=post_id, uid=usr.user.uid)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return resp_succ(new_post.to_resp())


@router.post("/update")
def update_post(
    new_post: UpdatePost,
    pid: str = Query(...),
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user),
):
    """Update a post"""
    post = db.get(Posts, pid)
    if not post:
        return resp_err(detail="Post not found", code=404)
    if post.uid != usr.user.uid:
        return resp_err(detail="You are not the owner of this post", code=403)
    if new_post.title is not None:
        post.title = new_post.title
    if new_post.content is not None:
        post.content = new_post.content
    if new_post.private is not None:
        post.private = new_post.private
    if new_post.status is not None:
        post.status = new_post.status
    post.updated = datetime.datetime.now()
    db.commit()
    db.refresh(post)
    return resp_succ(post.to_resp())


@router.delete("/{pid}")
def delete_post(
    pid: str,
    db: Session = Depends(get_db),
):
    post = db.get(Posts, pid)
    if not post:
        return resp_err(detail="Post not found", code=404)
    db.delete(post)
    db.commit()
    return resp_succ(detail="删除成功")


@router.get("/{pid}")
def get_post(
    pid: str,
    db: Session = Depends(get_db),
    usr: Optional[CurrentUser] = Depends(get_user_optional),
):
    """Get a post"""
    post = db.get(Posts, pid)
    if not post:
        return resp_err(detail="Post not found", code=404)
    return resp_succ(post.to_resp(True))
