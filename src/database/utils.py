from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from auth import get_user
from database import get_db
from database.models import RecipeIngredient, RecipeSteps, Recipes
from models import CurrentUser


def get_recipe(
    recipe_id: int, db: Session = Depends(get_db), usr: CurrentUser = Depends(get_user)
):
    recipe = db.exec(
        select(Recipes).where(Recipes.id == recipe_id, Recipes.uid == usr.user.id)
    ).one_or_none()
    if not recipe:
        raise HTTPException(
            status_code=404,
            detail="菜谱不存在或没有权限访问",
        )
    return recipe


def get_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user),
    exit_ok=False,
):
    ingredient = db.exec(
        select(RecipeIngredient)
        .join(Recipes)
        .where(
            RecipeIngredient.recipe_id == Recipes.id,
            Recipes.uid == usr.user.id,
            RecipeIngredient.id == ingredient_id,
        )
    ).one_or_none()
    if not ingredient and not exit_ok:
        raise HTTPException(status_code=404, detail="未找到该元素")
    return ingredient


def get_step(
    step_id: int,
    db: Session = Depends(get_db),
    usr: CurrentUser = Depends(get_user),
    exit_ok=False,
):
    step = db.exec(
        select(RecipeSteps)
        .join(Recipes)
        .where(
            RecipeSteps.recipe_id == Recipes.id,
            Recipes.uid == usr.user.id,
            RecipeSteps.id == step_id,
        )
    ).one_or_none()
    if not step and not exit_ok:
        raise HTTPException(status_code=404, detail="未找到该元素")
    return step
