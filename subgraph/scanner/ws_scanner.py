import asyncio
import websockets
import json
from collections import OrderedDict
from random import random
from websockets.exceptions import ConnectionClosedError
from config import VAULT, WS_RPC, EVENT_CONFIG, NETWORK2ID
from libs.logger import get_logger
from enum import Enum
from subgraph import handler as all_handlers
from subgraph.handler import raw_event_handler
from libs.utils import hex_to_address, get_object, keccak
from libs.chain import NetWork, Chain
from libs.redis import get_redis_async_connection

logger = get_logger(__name__)


class WSListenerState(Enum):
    INITIALISING = 'Initialising'
    STREAMING = 'Streaming'
    RECONNECTING = 'Reconnecting'
    EXITING = 'Exiting'


class WS_SCANNER:
    def __init__(self, chain):
        logger.info("work start")
        self.w3 = Chain(chain)
        self.chain_id = NETWORK2ID[chain]
        self.vault_address = VAULT['AddressOfVault']
        self.update_address = VAULT['AddressOfUpdate']

        self.ws_rpc = WS_RPC[VAULT['Chain']]
        self.ws_conn = None
        self.ws_state = WSListenerState.INITIALISING
        self.MAX_RECONNECTS = 10
        self._reconnects = 0

        self._connect_redis()

    async def _connect(self):
        try:
            self.ws_conn = await websockets.client.connect(self.ws_rpc)
            logger.info(self.ws_conn)
            await self.ws_conn.send(
                f"""
                    {{"jsonrpc": "2.0",
                     "id": 1,
                     "method": "eth_subscribe",
                     "params": [
                        "logs",
                        {{"address": ["{self.vault_address}", "{self.update_address}"],
                         "topics": []}}
                        ]
                     }}
                 """
            )

            subscription_response = await self.ws_conn.recv()
            logger.info(f"connect success {subscription_response}")
            self.ws_state = WSListenerState.STREAMING
            self._reconnects = 0
        except:
            await self._reconnect()
            return

    async def _reconnect(self):
        self.ws_state = WSListenerState.RECONNECTING

    def _get_reconnect_wait(self, attempts):
        expo = 2 ** attempts
        return round(random() * min(self.MAX_RECONNECT_SECONDS, expo - 1) + 1)

    async def _run_reconnect(self):
        if self._reconnects < self.MAX_RECONNECTS:
            reconnect_wait_time = self._get_reconnect_wait(self._reconnects)
            logger.info(
                f"websocket reconnecting. {self.MAX_RECONNECTS - self._reconnects} reconnects left - "
                f"waiting {reconnect_wait_time}"
            )
            await asyncio.sleep(reconnect_wait_time)
            await self._connect()
        else:
            logger.error(f'Max reconnections {self.MAX_RECONNECTS} reached:')
            # TODO raise error

    async def run(self):
        logger.info("start listen events")
        while True:
            # try:
            if self.ws_state == WSListenerState.RECONNECTING:
                await self._reconnect()
            if not self.ws_conn or self.ws_state != WSListenerState.STREAMING:
                await self._connect()
            elif self.ws_conn.state == websockets.protocol.State.CLOSING:  # type: ignore
                await asyncio.sleep(0.1)
                continue
            elif self.ws_conn.state == websockets.protocol.State.CLOSED:  # type: ignore
                await self._reconnect()
            if self.ws_state == WSListenerState.STREAMING:
                async for message in self.ws_conn:
                    logger.info(f"message {message}")
                    await self.handle_message(message)

        # except ConnectionClosedError as e:
        #     logger.error(f"connection close error ({e})")

        # except Exception as e:
        #     logger.error(f"Unknown exception ({e})")
        #     continue

    def _connect_redis(self):
        self.redis_client = get_redis_async_connection()

    def process_event(self, message):
        response = json.loads(message)
        logger.info(f"event response {response}")
        result = response['params']['result']
        event = OrderedDict()
        if result:
            event['block_hash'] = result['blockHash']
            event['block_number'] = int(result['blockNumber'], 16)
            event['contract_address'] = hex_to_address(result['address'])
            event['tx_hash'] = result['transactionHash']
            event['tx_index'] = int(result['transactionIndex'], 16)
            event['log_index'] = int(result['logIndex'], 16)
            event['data'] = result['data']
            block_info = self.w3.get_block(event['block_number'])
            event['block_time'] = block_info.timestamp
            for i in range(4):
                if i >= len(result['topics']):
                    event[f'topic{i}'] = ""
                else:
                    event[f'topic{i}'] = result['topics'][i]
            return event

    async def publish_to_redis(self, event):
        channel_name = f"{self.chain_id}_{event['contract_address']}"
        await self.redis_client.publish(channel_name, json.dumps(event))

    async def handle_message(self, message):
        event = self.process_event(message)
        logger.info(f"processed event {event}")
        if event:
            contract_address = event['contract_address']
            event_topic = event['topic0']
            logger.info(f"{contract_address} {event_topic}")
            await self.publish_to_redis(event)

            raw_event_handler(event, self)

    def start(self):
        asyncio.run(self.run())
