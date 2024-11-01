from fastapi import APIRouter

router = APIRouter(prefix="/ws", tags=["WebSocket"])

from . import main, file