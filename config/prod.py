import os
from .path import *

MYSQL_INFORMATION = {
    'host': 'prod-rubydex-cluster.cluster-cerd2x53mzqf.ap-southeast-1.rds.amazonaws.com',
    'user': 'chain',
    'password': 'Rt7@yzv0Ola59Izbv',
    'database': 'chain',
    'charset': 'utf8'
}


REDIS_CONFIG = {
    "host": "redis.host",
    "port": 6379,
    "password": "J+6Yfwr@9aj",
    "db": 0,
    "decode_responses": True
}

CHAIN = "arbitrum"
CHAIN_ID = 42161
START_BLOCK_NUMBER = 53852263

GRAPHQL_PORT = 6013
SOCKET_PORT = 6014

VAULT = {
    'Chain': 'arbitrum',
    'Abi': 'v1',
    'Tab': 'arbitrum-main',
    'AddressOfVault': '0xa55D96B2EC5c5899fC69886CACfCba65b91bf8B6',
    'AddressOfUpdate': '0xedB6CD4fdd2F465d2234f978276F9Ed2EE02102c',
    }
