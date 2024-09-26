from fastapi import APIRouter

router = APIRouter(prefix="/api")
from . import user, posts

routers = [
    user.router,
    posts.router
    # recipe.router
]
for r in routers:
    router.include_router(r)