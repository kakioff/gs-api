import datetime
import hashlib
import os
from typing import Optional
from fastapi import Depends, HTTPException, Request, Response, UploadFile
from sqlalchemy import func
from sqlmodel import Session, and_, or_, select

from auth import get_user, get_user_optional
from config import Settings, get_settings
from database import get_db
from database.models import RecipeGroups, RecipeIngredient, Recipes
from models import CurrentUser
from .models import CreateRecipe, CreateIngredient
from utils import resp_err, resp_succ
from . import router
from api import cos


def get_recipe(
    recipe_id: int, db: Session = Depends(get_db), usr: CurrentUser = Depends(get_user)
):
    recipe = db.exec(
        select(Recipes).where(Recipes.id == recipe_id, Recipes.uid == usr.user.id)
    ).one_or_none()
    if not recipe:
        raise HTTPException(
            status_code=404,
            detail="菜谱不存在或您没有权限访问",
        )
    return recipe


@router.get("/list")
async def list_recipes(
    db: Session = Depends(get_db),
    usr: Optional[CurrentUser] = Depends(get_user_optional),
):
    """
    获取全部菜谱
    """
    sql = select(Recipes)
    count_sql = select(func.count()).select_from(Recipes)

    if usr is not None:
        # 已登录用户
        sql_where = or_(
            and_(Recipes.private == True, Recipes.uid == usr.user.id),
            Recipes.private == False,  # 公开菜谱
        )
    else:
        # 未登录用户只能查看公开菜谱
        sql_where = or_(
            Recipes.private == False,
        )  # 公开菜谱

    sql = sql.where(sql_where)
    count_sql = count_sql.where(sql_where)

    all_counts = db.exec(count_sql).one()
    data = db.exec(sql).all()
    return resp_succ([item.to_resp() for item in data], total=all_counts)


@router.put("/create")
def create_recipe(
    recipe: CreateRecipe,
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user),
):
    """
    创建菜谱
    """
    new_recipe = Recipes(uid=usr.user.id, **recipe.model_dump())
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return resp_succ(new_recipe)


@router.post("/update")
def update_recipe(
    opts: CreateRecipe,
    recipe: Recipes = Depends(get_recipe),
    db: Session = Depends(get_db),
):
    """
    更新菜谱
    """
    if opts.gid is not None:
        recipe_group = db.exec(
            select(RecipeGroups)
            .where(RecipeGroups.id == opts.gid)
            .where(RecipeGroups.uid == recipe.uid)
        ).one_or_none()
        if not recipe_group:
            return resp_err(
                "分组不存在或您没有权限访问",
                code=404,
            )
        recipe.gid = opts.gid
    if opts.name is not None:
        recipe.name = opts.name
    if opts.desc is not None:
        recipe.desc = opts.desc
    if opts.status is not None:
        recipe.status = opts.status
    if opts.private is not None:
        recipe.private = opts.private
    recipe.updated = datetime.datetime.now()
    db.add(recipe)
    return resp_succ(recipe.to_resp())


@router.get("/item")
def get_recipe_detail(recipe: Recipes = Depends(get_recipe)):
    data = recipe.to_resp()
    data.update(
        {
            "steps": [step.to_resp() for step in recipe.all_steps()],
            "comments": [comment.to_resp() for comment in recipe.comments],
        }
    )
    return resp_succ(data)


@router.delete("/delete")
def delete_recipe(recipe: Recipes = Depends(get_recipe), db: Session = Depends(get_db)):
    db.delete(recipe)
    return resp_succ(detail="删除成功")


@router.post("/cover")
def update_recipe_cover(
    file: UploadFile,
    settings: Settings = Depends(get_settings),
    usr: CurrentUser = Depends(get_user),
    recipe: Recipes = Depends(get_recipe),
):
    # 生成文件名
    file_name = hashlib.md5(file.file.read()).hexdigest() + ".png"
    cos_path = os.path.join(
        "recipe",
        f"user_{usr.user.id}",
        f"recipe_{recipe.id}",
        "cover",
        file_name,
    )
    # 重置
    file.file.seek(0)
    local_path = settings.temp_dir + file_name
    # 临时保存
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(file.file.read())
    # 上传
    cos.upload_file(local_path, cos_path)
    # region 删除缓存文件
    if os.path.exists(local_path):
        os.remove(local_path)
    # endregion
    recipe.cover = cos_path
    return resp_succ(detail="上传成功")


@router.get("/cover")
def get_recipe_cover(recipe: Recipes = Depends(get_recipe)):
    if not recipe.cover:
        return resp_err(code=404, detail="封面不存在")
    cover = cos.get_file(recipe.cover)
    return Response(content=cover, media_type="image/png")


@router.post("/ingredient")
def update_recipe_ingredient(
    ingredient: CreateIngredient,
    recipe: Recipes = Depends(get_recipe),
    db: Session = Depends(get_db),
):
    if not ingredient.name:
        return resp_err(code=400, detail="名称不能为空")
    new_ing = RecipeIngredient(
        recipe_id=recipe.id,
        **ingredient.model_dump(),
    )
    db.add(new_ing)
    db.commit()
    db.refresh(new_ing)
    return resp_succ(new_ing.to_resp())
