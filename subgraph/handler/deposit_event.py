
from libs.db_mysql import db_session
from libs.logger import get_logger
from subgraph.repo import DepositEventRepo
from web3 import Web3
from libs.utils import hex_to_address

logger = get_logger(__name__)

def deposit_event_handler(event, context):
    with db_session() as session:
        deposit_event_repo = DepositEventRepo(session)
        deposit_event_repo.create_if_not_exist(
            tx_hash = event['tx_hash'],
            block_number = event['block_number'],
            block_time = event['block_time'],
            token = hex_to_address(event['topic1']),
            account = hex_to_address(event['topic2']),
            amount = Web3.toInt(hexstr=event['data'])
        )

        
