""" 
文件传输的ws
"""

import json
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from .models import ConnectManager

from . import router as f_router

managers = ConnectManager()

router = APIRouter(prefix="/file", tags=["WebsocketFile"])


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Query(...),
    room_id: str = Query(default=None),
):
    await managers.connect(websocket, client_id, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            msg_type = data.get("type")
            send_to = data.get("to")

            if msg_type == "getUserList":
                all_connets = managers.get_all_clients(room_id)
                await websocket.send_json(
                    {
                        "type": "userList",
                        "data": [c.client_id for c in all_connets],
                        "total": len(all_connets),
                    }
                )
            elif msg_type == "message":
                if send_to is None or send_to == "all":
                    await managers.broadcast(
                        websocket,
                        json.dumps({"from": client_id, **data}, ensure_ascii=False),
                        room_id=room_id,
                    )
                else:
                    await managers.send_personal_message(
                        websocket,
                        send_to,
                        json.dumps({"from": client_id, **data}, ensure_ascii=False),
                    )
    except WebSocketDisconnect:
        managers.disconnect(client_id)


f_router.include_router(router)
