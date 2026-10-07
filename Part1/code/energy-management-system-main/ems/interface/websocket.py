from fastapi import WebSocket, WebSocketDisconnect, Depends
import asyncio
from ems.interface.runtime import get_runtime, EMSRuntime


async def ws_endpoint(
    ws: WebSocket, dispatcher: EMSRuntime = Depends(get_runtime)
):
    """WebSocket endpoint for live EMS context updates"""
    await ws.accept()
    async with dispatcher._subscribers_lock:
        dispatcher.subscribers.append(ws)
    try:
        while True:
            try:
                await asyncio.wait_for(ws.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        async with dispatcher._subscribers_lock:
            if ws in dispatcher.subscribers:
                dispatcher.subscribers.remove(ws)
