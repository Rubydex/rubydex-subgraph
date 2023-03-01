import os
from libs.logger import get_logger
from dataclasses import dataclass, field
from typing import List
from libs.utils import hex_to_address
import strawberry
from web3 import Web3
from eth_abi import decode

logger = get_logger(__name__)

    
@strawberry.type
@dataclass
class LogPositionChangeEntity():
    tx_hash: str = ""
    block_number: int = 0
    block_time: int = 0
    account: str = ""
    asset: str = ""
    volume: int = 0
    lastCumulativeFundingPerVolume: int = 0
    entryCost: int = 0


class LogPositionChangeEvent():
    
    def __init__(self, event):
        self.name = self.__class__.__name__
        self.event = event
        (account, asset, volume, lastCumulativeFundingPerVolume, entryCost) = decode(["address","bytes32","int64", "int64", "int128"], Web3.toBytes(hexstr=event['data']))
        event['account'] = account
        event['asset'] = asset
        event['volume'] = volume
        event['lastCumulativeFundingPerVolume'] = lastCumulativeFundingPerVolume
        event['entryCost'] = entryCost
        

    def __repr__(self):
        return f"<{self.name}(tx_hash={self.event['tx_hash']})>"

    def to_entity(self) -> LogPositionChangeEntity:
        props = LogPositionChangeEntity.__dataclass_fields__.keys()
        kv = {prop: self.event[prop] for prop in props}
        return LogPositionChangeEntity(**kv)


