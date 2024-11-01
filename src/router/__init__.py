from fastapi import APIRouter, WebSocket

router = APIRouter(prefix="/api")
from . import user, posts, files, main, websocket

routers = [
    user.router,
    posts.router,
    files.router,
    websocket.router,
    # recipe.router
]
for r in routers:
    router.include_router(r)