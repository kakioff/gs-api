from typing import Optional
from fastapi import Depends
from sqlalchemy import func
from sqlmodel import Session, or_, select
from auth import get_user_optional
from database import get_db
from database.models import Recipes
from models import CurrentUser
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
        sql = sql.where(or_(Recipes.private == False, Recipes.uid == usr.user.id))
        count_sql = count_sql.where(or_(Recipes.private == False, Recipes.uid == usr.user.id))
    else:
        sql = sql.where(Recipes.private == False)
        count_sql = count_sql.where(Recipes.private == False)
    all_counts = db.exec(count_sql).one()
    data = db.exec(sql).all()
    return resp_succ(data, total=all_counts)

@router.put("/create")
def create_recipe(recipe: Recipes, db: Session = Depends(get_db)):
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return resp_succ(recipe)