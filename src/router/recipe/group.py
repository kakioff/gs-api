from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, and_, or_, select

from auth import get_user, get_user_optional
from database import get_db
from database.models import RecipeGroups
from models import CurrentUser
from router.recipe.models import CreateRecipeGroup
from utils import resp_err, resp_succ

from . import router as recipe_router

router = APIRouter(tags=["Recipe", "RecipeGroup"])


def get_recipe_group(
    group_id: int, db: Session = Depends(get_db), usr: CurrentUser = Depends(get_user)
):
    recipe = db.exec(
        select(RecipeGroups).where(
            RecipeGroups.id == group_id, RecipeGroups.uid == usr.user.id
        )
    ).one_or_none()
    if not recipe:
        raise HTTPException(
            status_code=404,
            detail="菜谱不存在或您没有权限访问",
        )
    return recipe


def get_recipe_group_optional(
    group_id: int | None = None,
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user),
):
    if not group_id:
        return None
    return get_recipe_group(group_id, db, usr)


@router.get("/list")
async def get_group_list(
    usr: CurrentUser = Depends(get_user_optional), db: Session = Depends(get_db)
):
    if usr:
        sql_where = or_(
            RecipeGroups.private == False,
            and_(RecipeGroups.uid == usr.user.id, RecipeGroups.private == True),
        )
    else:
        sql_where = or_(RecipeGroups.private == False)
    groups = db.exec(select(RecipeGroups).where(sql_where)).fetchall()
    groups = [group.to_resp() for group in groups]
    return resp_succ(groups)


@router.get("/recipes")
async def get_recipes_from_group(
    group: RecipeGroups = Depends(get_recipe_group),
):
    recipes = group.recipes
    recipes = [recipe.to_resp() for recipe in recipes]
    return resp_succ(recipes)


@router.get("/children")
async def get_group_children(
    group: Union[RecipeGroups, None] = Depends(get_recipe_group_optional),
    db: Session = Depends(get_db),
):
    if group:
        group_list = [g.to_resp() for g in group.children]
    else:
        group_list = db.exec(
            select(RecipeGroups).where(RecipeGroups.parent_id == None)
        ).fetchall()
        group_list = [g.to_resp() for g in group_list]
    return resp_succ(group_list)


@router.post("/create")
async def create_group(
    group: CreateRecipeGroup,
    usr: CurrentUser = Depends(get_user_optional),
    db: Session = Depends(get_db),
):
    if group.parent_id:
        parent_group = db.exec(
            select(RecipeGroups).where(RecipeGroups.id == group.parent_id)
        ).one_or_none()
        if not parent_group:
            return resp_err(detail="父文件夹不存在")
    new_group = RecipeGroups(uid=usr.user.id, **group.model_dump())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return resp_succ(new_group.to_resp())


@router.post("/update")
async def update_group(
    opts: CreateRecipeGroup,
    group: RecipeGroups = Depends(get_recipe_group),
    db: Session = Depends(get_db),
):
    if opts.parent_id:
        if opts.parent_id == group.id:
            return resp_err(detail="不能将文件夹移动到自身")

        # 检查父文件夹是否存在
        parent_group = db.exec(
            select(RecipeGroups).where(RecipeGroups.id == opts.parent_id)
        ).one_or_none()
        if not parent_group:
            return resp_err(detail="父文件夹不存在")
        group.parent_id = opts.parent_id
    if opts.name:
        group.name = opts.name
    if opts.desc:
        group.desc = opts.desc
    if opts.status:
        group.status = opts.status
    if opts.private:
        group.private = opts.private
    db.add(group)
    db.commit()
    db.refresh(group)
    return resp_succ(group.to_resp())


# 添加子路由
recipe_router.include_router(router, prefix="/group")
