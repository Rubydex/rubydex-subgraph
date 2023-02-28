
from libs.db_mysql import db_session
from libs.logger import get_logger
from subgraph.repo import WithdrawEventRepo
from web3 import Web3
from libs.utils import hex_to_address
from eth_abi import decode

logger = get_logger(__name__)

def withdraw_event_handler(event, context):
    with db_session() as session:
        withdraw_event_repo = WithdrawEventRepo(session)
        (amount, expiry, nonce) = decode(["uint256","uint256","uint256"], Web3.toBytes(hexstr=event['data']))
        withdraw_event_repo.create_if_not_exist(
            tx_hash = event['tx_hash'],
            block_number = event['block_number'],
            block_time = event['block_time'],
            token = hex_to_address(event['topic1']),
            account = hex_to_address(event['topic2']),
            amount = amount,
            expiry = expiry,
            nonce = nonce
        )

        
