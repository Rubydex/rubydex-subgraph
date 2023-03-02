import asyncio
import websockets
import json
from collections import OrderedDict
from random import random
from websockets.exceptions import ConnectionClosedError
from config import VAULT, EVENT_CONFIG, START_BLOCK_NUMBER
from libs.logger import get_logger
from enum import Enum
from subgraph import handler as all_handlers
from subgraph.handler import raw_event_handler
from libs.utils import hex_to_address, get_object, keccak
from libs.chain import NetWork, Chain
from libs.db_mysql import db_session, check_databases, check_table_exist

logger = get_logger(__name__)


def check_update_table():
    create_sql = """
        CREATE TABLE updated_blocknumber
        (
            id                  int primary key auto_increment,
            contract_address    VARCHAR(42) NOT NULL UNIQUE,
            block_number        INT(20) NOT NULL
        );
    """
    with db_session() as db:
        check_databases(db, set(["chain"]))
        if not check_table_exist(db, "chain", "updated_blocknumber"):
            db.execute(create_sql)


def get_last_block_number(contract_address):
    sql = f"""
        select * from updated_blocknumber where contract_address='{contract_address}'
    """
    with db_session() as db:
        db.execute(sql)
        res = db.get_dicts()
        if res:
            return res[0]['block_number']
        else:
            return START_BLOCK_NUMBER


def update_last_block_number(contract_address, last_block_number):
    sql = f"""
        INSERT INTO updated_blocknumber (contract_address, block_number)
        VALUES ('{contract_address}', {last_block_number})
        ON DUPLICATE KEY UPDATE block_number = {last_block_number};
    """
    with db_session() as db:
        db.execute(sql)


class BATCH_SCANNER:

    def __init__(self, chain):
        logger.info("work start")
        self.w3 = Chain(chain)
        self.vault_address = VAULT['AddressOfVault']
        self.update_address = VAULT['AddressOfUpdate']

        check_update_table()

    async def run(self):
        logger.info("start listen events")
        start_block_number = min(
            get_last_block_number(hex_to_address(self.vault_address)),
            get_last_block_number(hex_to_address(self.update_address))
        )
        addresses = [hex_to_address(self.vault_address), hex_to_address(self.update_address)]
        topics = []
        cur_block_number = self.w3.get_block_number()
        iter_num = (cur_block_number - start_block_number) // 10000 + 1
        for i in range(iter_num):
            from_block = start_block_number + i * 10000
            to_block = from_block + 10000
            if to_block >= cur_block_number:
                to_block = cur_block_number

            result = self.w3.get_batch_events(addresses, topics, from_block, to_block)
            logger.info(f"fetch batch events num: {len(result)}")
            for message in result:
                await self.handle_message(message)

            update_last_block_number(hex_to_address(self.vault_address), to_block)
            update_last_block_number(hex_to_address(self.update_address), to_block)

    def process_event(self, result):
        # logger.info(f"message {result}")
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

    async def handle_message(self, message):
        event = self.process_event(message)
        if event:
            contract_address = event['contract_address']
            event_topic = event['topic0']
            logger.info(f"{contract_address} {event_topic}")

            raw_event_handler(event, self)

    def start(self):
        asyncio.run(self.run())
