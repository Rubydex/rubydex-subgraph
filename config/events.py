from config import VAULT, CHAIN_ID
from libs.utils import keccak
EVENTS = [
            {
                'chain_id': CHAIN_ID,
                'address': VAULT['AddressOfVault'],
                'abi_name': "VaultImplementation",
                'event_name': 'Deposit(address,address,uint256)'
            },
            {
                'chain_id': CHAIN_ID,
                'address': VAULT['AddressOfVault'],
                'abi_name': "VaultImplementation",
                'event_name': 'Withdraw(address,address,uint256,uint256,uint256)'
            },
            {
                'chain_id': CHAIN_ID,
                'address': VAULT['AddressOfVault'],
                'abi_name': "VaultImplementation",
                'event_name': 'CreateRequestWithdraw(uint256,address,address,bytes)'
            },
            {
                'chain_id': CHAIN_ID,
                'address': VAULT['AddressOfVault'],
                'abi_name': "VaultImplementation",
                'event_name': 'ExecuteWithdraw(uint256,address,address,bytes)'
            },
            {
                'chain_id': CHAIN_ID,
                'address': VAULT['AddressOfVault'],
                'abi_name': "VaultImplementation",
                'event_name': 'CancelWithdraw(uint256,address,address,bytes)'
            },
            {
                'chain_id': CHAIN_ID,
                'address': VAULT['AddressOfUpdate'],
                'abi_name': "UpdateStateImplementation",
                'event_name': 'LogBalanceChange(address,address,int256)'
            },
            {
                'chain_id': CHAIN_ID,
                'address': VAULT['AddressOfUpdate'],
                'abi_name': "UpdateStateImplementation",
                'event_name': 'LogPositionChange(address,bytes32,int64,int64,int128)'
            },
        ]


def get_events_config():
    for event in EVENTS:
        event['signature'] = keccak(event['event_name'])
    return EVENTS
    
    
    
EVENT_CONFIG = get_events_config()