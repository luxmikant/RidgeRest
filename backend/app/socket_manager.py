import socketio

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],  # Will be set from config
    logger=False,
    engineio_logger=False,
)


@sio.event
async def connect(sid, environ):
    pass


@sio.event
async def join(sid, data):
    """Employee joins their personal room to receive status updates."""
    room = data.get("user_id")
    if room:
        sio.enter_room(sid, room)


@sio.event
async def disconnect(sid):
    pass
