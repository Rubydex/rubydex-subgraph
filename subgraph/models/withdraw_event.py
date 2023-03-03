import os
from libs.logger import get_logger
from dataclasses import dataclass, field
from typing import List
from eth_abi import decode
from web3 import Web3
from libs.utils import hex_to_address
import strawberry


logger = get_logger(__name__)

@strawberry.type
@dataclass
class WithdrawEventEntity():
    tx_hash: str = ""
    block_number: int = 0
    block_time: int = 0 
    token: str = ""
    account: str = ""
    amount: str = ""
    expiry: int = 0
    nonce: int = 0


class WithdrawEvent():
    
    def __init__(self, event):
        self.name = self.__class__.__name__
        self.event = event
        (amount, expiry, nonce) = decode(["uint256","uint256","uint256"], Web3.toBytes(hexstr=event['data']))
        event['token'] = hex_to_address(event['topic1'])
        event['account'] = hex_to_address(event['topic2'])
        event['amount'] = amount
        event['expiry'] = expiry
        event['nonce'] = nonce

    def __repr__(self):
        return f"<{self.name}(tx_hash={self.event['tx_hash']})>"

    def to_entity(self) -> WithdrawEventEntity:
        props = WithdrawEventEntity.__dataclass_fields__.keys()
        kv = {prop: self.event[prop] for prop in props}
        return WithdrawEventEntity(**kv)