import asyncio
import json
from fastapi.applications import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import async_timeout
import socketio
import uvicorn
from config import EVENT_CONFIG, CHAIN_ID
from libs.logger import get_logger
from libs.redis import get_redis_async_connection

origins = [
        'http://localhost:3000',
        '*',
        ]

logger = get_logger(__name__)

def normalize_data(data_str):
    try:
        data = json.loads(data_str)
    except Exception as ex:
        logger.error(f"normalize_data error: {ex}")
    return data_str

class Pusher:
    def __init__(self, sio):
        self.sio = sio
        self.cache = {}
        self._init_channel()
        self._connect_redis()

    def _connect_redis(self):
        self.redis_client = get_redis_async_connection()
        self.pubsub = self.redis_client.pubsub()

    def _init_channel(self):
        self.channels = set()
        for event in EVENT_CONFIG:
            self.channels.add(f"{CHAIN_ID}_{event['address']}")
        logger.info(f"init_channel {self.channels}")

    async def get(self, key):
        try:
            res = await self.redis_client.get(key)
            return normalize_data(res)
        except Exception as ex:
            logger.error(f"Pusher#get({key}) error: {ex}")
        return None

    # pubsub
    async def read_sub(self):
        # subscribe channels
        await self.pubsub.subscribe(*self.channels)

        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                    if message is not None:
                        print(f"Message received: {message}")
                        channel, data = message['channel'], message['data']
                        await self.sio.emit(channel, normalize_data(data), room=channel)
                await asyncio.sleep(0.05)
            except asyncio.TimeoutError as ex:
                logger.error(f"Pusher#read_sub error: {ex}")

# app

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=origins)
redis_client = get_redis_async_connection()
pusher = Pusher(sio)
sio.start_background_task(pusher.read_sub)
app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        )

@app.get('/')
async def home():
    return {"message": "Hello!"}



@app.get('/channels/{channel}')
async def get_channel_data(channel:str):
    res = await redis_client.get(channel)
    if res:
        try:
            return json.loads(res)
        except Exception as ex:
            logger.error(f"get_channel_data error: {ex}")
    return res or {}

socket_app = socketio.ASGIApp(
        socketio_server = sio,
        socketio_path = 'socket.io'
        )

app.mount('/', socket_app)



@sio.event
async def connect(sid, environ):
    print('-- connnect', sid)


@sio.event
def disconnect(sid):
    print('-- disconnnect', sid)
    

@sio.event
async def add_channel(sid, opts={}):
    logger.info(f"opts {opts}")
    channel_name = opts['channel']
    print(f"-- add_channel({sid}): {channel_name}")
    if channel_name:
        sio.enter_room(sid, channel_name)
        res = await pusher.get(channel_name)
        if res:
            await sio.emit(channel_name, res, room=channel_name)

        # await sio.emit(channel_name, f"hello from {channel_name}", room=channel_name)

@sio.on('*')
async def catch_all(event, sid, data):
    pass

if __name__ == "__main__":
    # web.run_app(init_app(), port=9002)
    kwargs = { "host": "0.0.0.0", "port": 6014}
    uvicorn.run("ws_server:app", **kwargs)

