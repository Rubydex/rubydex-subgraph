import os
from libs.logger import get_logger
from dataclasses import dataclass, field
from typing import List
import strawberry
from web3 import Web3
from libs.utils import hex_to_address

logger = get_logger(__name__)


@strawberry.type
@dataclass
class DepositEventEntity():
    tx_hash: str = ""
    block_number: int = 0
    block_time: int = 0
    token: str = ""
    account: str = ""
    amount: str = ""


class DepositEvent():
    
    def __init__(self, event):
        self.name = self.__class__.__name__
        self.event = event
        event['token'] = hex_to_address(event['topic1'])
        event['account'] = hex_to_address(event['topic2'])
        event['amount'] = Web3.toInt(hexstr=event['data'])

    def __repr__(self):
        return f"<{self.name}(tx_hash={self.event['tx_hash']})>"

    def to_entity(self) -> DepositEventEntity:
        props = DepositEventEntity.__dataclass_fields__.keys()
        kv = {prop: self.event[prop] for prop in props}
        return DepositEventEntity(**kv)




