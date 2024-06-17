from fastapi import APIRouter

router = APIRouter(prefix="/recipe", tags=["Recipe"])

from . import main