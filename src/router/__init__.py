from fastapi import APIRouter

router = APIRouter(prefix="/api")
from . import user, recipe

routers = [
    user.router,
    recipe.router
]
for r in routers:
    router.include_router(r)