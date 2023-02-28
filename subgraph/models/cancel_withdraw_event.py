import os
from libs.logger import get_logger
from dataclasses import dataclass, field
from typing import List
from libs.utils import hex_to_address
import strawberry


logger = get_logger(__name__)


@strawberry.type
@dataclass
class CancelWithdrawEntity():
    tx_hash: str = ""
    block_number: int = 0
    block_time: int = 0
    withdrawIndex: int = 0
    account: str = ""
    token: str = ""
    signatures: str = ""


class CancelWithdrawEvent():
    
    def __init__(self, event):
        self.name = self.__class__.__name__
        self.event = event
        event['withdrawIndex'] = int(event['topic1'], 16)
        event['account'] = hex_to_address(event['topic2'])
        event['token'] = hex_to_address(event['topic3'])
        event['signatures'] = event['data']


    def __repr__(self):
        return f"<{self.name}(tx_hash={self.event['tx_hash']})>"

    def to_entity(self) -> CancelWithdrawEntity:
        props = CancelWithdrawEntity.__dataclass_fields__.keys()
        kv = {prop: self.event[prop] for prop in props}
        return CancelWithdrawEntity(**kv)


