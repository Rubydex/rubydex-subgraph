import os
from .path import *

MYSQL_INFORMATION = {
    'host': 'prod-rubydex-cluster.cluster-cerd2x53mzqf.ap-southeast-1.rds.amazonaws.com',
    'user': 'dc',
    'password': 'e1c3d578280db36d6acf698359dc5ea8',
    'database': 'dc',
    'charset': 'utf8'
}

CHAIN_ID = 42161
START_BLOCK_NUMBER = 53852263

VAULT = {
    'Chain': 'arbitrum',
    'Abi': 'v1',
    'Tab': 'arbitrum-test-main',
    'AddressOfVault': '0xa55D96B2EC5c5899fC69886CACfCba65b91bf8B6',
    'AddressOfUpdate': '0xedB6CD4fdd2F465d2234f978276F9Ed2EE02102c',
    }
