from fastapi import APIRouter

router = APIRouter(prefix="/api")
from . import user

routers = [
    user.router
]
for r in routers:
    router.include_router(r)