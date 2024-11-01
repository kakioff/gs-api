from fastapi import APIRouter

router = APIRouter(prefix="/file", tags=["File"])

from . import main