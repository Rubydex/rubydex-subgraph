import asyncio
import json
from time import time
import socketio
import argparse

def get_channel_name(channel_dict):
    return f"{channel_dict['chain_id']}_{channel_dict['contract_address']}"


async def main(sio, url):
    await sio.connect(url)
    await sio.wait()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('channel', nargs='?', default='{"chain_id":"421613", "contract_address":"0x0423c54736d12f445111a529A6c558953E469144"}')
    parser.add_argument('url',     nargs='?', default=f"http://localhost:9002")
    args = parser.parse_args()
    print(args)

    url = args.url
    channel = args.channel
    try:
        channel = json.loads(channel)
        # channel_name = f"{channel['chain_id']}_{channel['event']}"
        channel_name = get_channel_name(channel)
        print(f'-- channel_name: {channel_name}')
    except:
        pass


    sio = socketio.AsyncClient()

    last_time = time()

    @sio.event
    async def connect():
        print('connection established')
        await sio.emit('add_channel', {"channel":channel_name})


    @sio.event
    async def connect_error(data):
        print('connection failed!')

    @sio.event
    async def disconnect():
        print('disconnected from server')

    @sio.event
    async def message(data):
        print(data)
        print('hi')

    @sio.on(channel_name)
    async def on_message(data):
        global last_time
        now = time()
        print(f"-- {channel_name}: {json.dumps(data, indent=2)} ({now - last_time:>6.2f}s)")
        last_time = now

    asyncio.run(main(sio, url))
