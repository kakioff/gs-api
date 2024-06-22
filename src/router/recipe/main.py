from typing import Optional
from fastapi import Depends
import orjson
from sqlalchemy import ColumnElement, func
from sqlmodel import Session, and_, or_, select
from auth import get_user, get_user_optional
from database import get_db
from database.models import Recipes
from models import CurrentUser
from router.recipe.models import CreateRecipe
from utils import resp_succ
from . import router


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
    recipe_json = {
        **recipe.model_dump(),
        "materials": orjson.dumps(recipe.materials).decode(),
    }
    new_recipe = Recipes(uid=usr.user.id, **recipe_json)
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return resp_succ(new_recipe)
