import datetime
from typing import Optional
from fastapi import Depends, Query
from sqlmodel import Session, or_, select
from auth import get_user, get_user_optional
from database import get_db
from database.models import Posts
from models import CurrentUser
from router.posts.models import CreatePost
from utils import resp_err, resp_succ
from . import router


@router.get("/all")
def all_posts(
    page: int = Query(1),
    limit: int = Query(10),
    mine: bool = Query(False),
    search: str = Query(None),
    sort: str = Query("created"),
    db: Session = Depends(get_db),
    console: bool = Query(False),
    usr: Optional[CurrentUser] = Depends(get_user_optional),
):
    """Get all posts"""
    page = page - 1

    sql = select(Posts)
    if not console:
        sql = sql.where(Posts.status == 1)
        zusr_sql = Posts.private == False
        if usr:
            zusr_sql = or_(zusr_sql, Posts.uid == usr.user.id)
        sql = sql.where(zusr_sql)
    elif usr:
        sql = sql.where(Posts.uid == usr.user.id)

    if search:
        sql_where = or_(search in Posts.title, search in Posts.content)
        sql = sql.where(sql_where)

    posts = db.exec(
        sql.order_by(sort).offset(page * limit).limit(limit)
    ).all()
    return resp_succ([post.to_resp() for post in posts])

@router.put("/create")
def create_post(
    new_post_conf: CreatePost,
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user),
):
    """Create a post"""
    new_post = Posts(**new_post_conf.dict(), uid=usr.user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return resp_succ(new_post.to_resp())
    
@router.post("/update")
def update_post(
    new_post: CreatePost,
    pid: int = Query(...),
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user),
):
    """Update a post"""
    post = db.get(Posts, pid)
    if not post:
        return resp_err(detail="Post not found", code=404)
    post.title = new_post.title
    post.content = new_post.content
    post.private = new_post.private
    post.status = new_post.status
    post.updated = datetime.datetime.now()
    db.commit()
    db.refresh(post)
    return resp_succ(post.to_resp())
    
    
@router.delete("/{pid}")
def delete_post(
    pid: int,
):
    """Delete a post"""
    pass
@router.get("/{pid}")
def get_post(
    pid: int,
    db: Session = Depends(get_db),
    usr: Optional[CurrentUser] = Depends(get_user_optional),
):
    """Get a post"""
    post = db.get(Posts, pid)
    if not post:
        return resp_err(detail="Post not found", code=404)
    return resp_succ(post.to_resp(True))