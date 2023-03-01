import copy
import inspect
import json
import multiprocessing.pool as mpp
import os
import random
import threading
import time
import traceback

import requests
from eth_typing import ChecksumAddress
from web3 import Web3
from web3 import exceptions
from web3.middleware import geth_poa_middleware, local_filter_middleware

from config import RPCS, ABIS_PATH, NETWORK2ID
from libs.logger import get_logger
from libs.utils import retry_with_web3
from web3._utils.request import make_post_request
from web3._utils.encoding import FriendlyJsonSerde
from eth_utils import to_bytes, to_text


logger = get_logger(__name__)

web3_errors = tuple([error for name, error in inspect.getmembers(exceptions) if
                     inspect.isclass(error) and issubclass(error, Exception)])


def single_chain(cls):
    """
    装饰器用于每个链生成单例
    @param cls:
    @return:
    """
    networks = {}

    def _single_chain(*args, **kargs):
        network = args[0]
        if network not in networks:
            chain = cls(*args, **kargs)
            networks[network] = chain
            return chain
        else:
            return networks[args[0]]

    return _single_chain


def single_abi(cls):
    """
    装饰器用于每个abi生成单例
    @param cls:
    @return:
    """
    abis = {}

    def _single_chain(*args, **kargs):
        abi_dir = args[0]
        abi_name = args[1]
        sign = (abi_dir, abi_name)
        if sign not in abis:
            abi = cls(*args, **kargs)
            abis[sign] = abi
            return abi
        else:
            return abis[sign]

    return _single_chain


def single_address(cls):
    """
    装饰器用于每个地址生成单例
    @param cls:
    @return:
    """
    addresses = {}

    def _single_address(*args, **kargs):
        address = args[0].lower
        if address not in addresses:
            address_obj = cls(*args, **kargs)
            addresses[address] = address_obj
            return address_obj
        else:
            return addresses[address]

    return _single_address


def error_retrying(fun):
    """
    装饰器，用于与链交互时发生错误后刷新rpc，并重新交互
    @param fun:
    @return:
    """

    def wrapper(*args, times=10, **kwargs):
        try:
            res = fun(*args, **kwargs)
        except web3_errors as e:
            chain = get_chain(args[0])
            logger.error(f'Rpcs[{chain.Name}]<{fun.__name__}>Web3_errors: {e}')
            raise e
        except TypeError as e:
            chain = get_chain(args[0])
            logger.error(f'Rpcs[{chain.Name}]<{fun.__name__}>Web3_errors: {e}')
            raise e
        except (requests.exceptions.HTTPError, requests.exceptions.ReadTimeout) as e:
            chain = get_chain(args[0])
            logger.warning(f'Rpcs[{chain.Name}]<{fun.__name__}>Web3_errors: {e}')
            times = times - 1
            if times:
                logger.warning(f'Rpcs[{chain.Name}]<{fun.__name__}>Error: {e}')

                chain.refresh_rpc(url=chain.Rpc)
                return wrapper(*args, times=times, **kwargs)
            else:
                logger.error(f'Rpcs[{chain.Name}]<{fun.__name__}>Retrying failed: {e}')
                time.sleep(10 * 60)
                return wrapper(*args, times=1, **kwargs)
        return res

    return wrapper


def get_chain(args0):
    if isinstance(args0, _Chain):
        return args0
    else:
        return args0.Chain


class _Chain:
    Name: str
    ChainId: int
    AllRpcs: set
    AliveRpcs: set
    Rpc: str

    def __init__(self, name: str, rpcs: set = None, thread_of_refresh_rpc=True):
        self.ChainId = NETWORK2ID[name]
        self.Name = name
        self.AllRpcs = rpcs if rpcs else RPCS[name]
        self.AliveRpcs = copy.deepcopy(self.AllRpcs)
        self.Rpc = ''
        logger.cyan(f'Chain[{self.Name}] Init.')
        if thread_of_refresh_rpc:
            self.refresh_rpc()
            threading.Thread(target=self.thread_of_refresh_rpcs, daemon=True).start()

    def thread_of_refresh_rpcs(self):
        """
        线程，定时刷新rpc
        @return:
        """
        while True:
            time.sleep(15 * 60)
            try:
                self.refresh_rpc()
            except Exception as e:
                logger.error(f'Chain[{self.Name}]<thread_of_refresh_rpcs>{e}')

    def get_rpc(self):
        """
        随机获取rpc
        @return:
        """
        rpc = random.choice(list(self.AliveRpcs))
        return rpc

    @error_retrying
    def get_web3(self, geth_poa: bool = True, local_filter: bool = True) -> Web3:
        """
        获取web3对象
        @param geth_poa: Geth的PoA使用了超过32个字节,因此这个中间件在返回块数据之前对其进行了一些修改
        @param local_filter:太坊节点管理过滤器的替代方案，日志和块过滤器逻辑在本地处理
        @return: web3对象
        """
        rpc = self.get_rpc()
        self.Rpc = rpc
        web3 = Web3(Web3.HTTPProvider(rpc))
        if geth_poa:
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if local_filter:
            web3.middleware_onion.add(local_filter_middleware)
        web3.rpc = rpc
        return web3

    @error_retrying
    def get_block(self, number='latest'):
        """
        获取 块
        @param number: latest(default)
        @return: 块
        """
        web3 = self.get_web3()
        block = web3.eth.get_block(number)
        return block

    @error_retrying
    def get_block_number(self):
        web3 = self.get_web3()
        block_number = web3.eth.get_block_number()
        return block_number

    @error_retrying
    def get_transaction(self, tx_hash):
        web3 = self.get_web3()
        transaction = web3.eth.get_transaction(tx_hash)
        return transaction

    
    @error_retrying
    def get_blocks(self, numbers, threads=10):
        """
        获取多个块
        @param numbers: iterable
        @param threads: 线程(default：10)
        @return:
        """
        if not numbers:
            return []
        web3 = self.get_web3()
        pool = mpp.ThreadPool(threads)
        res = pool.map(web3.eth.getBlock, numbers)
        return res

    def refresh_rpc(self, geth_poa: bool = True, local_filter: bool = True, url: str = None, min_block_number=None,
                    times: int = 5):
        """
        刷新rpc，规则：
        初始化：生成白名单—全部配置里的rpc
        刷新：剔除传入的rpc，获取全部配置里的rpc的最新block，比较白名单里的block，白名单里与最新block差距较大的剔除
        重置：当白名单为空时，重置白名单（全部配置里的rpc），然后重复以上步骤
        @param geth_poa:
        @param local_filter:
        @param url: 剔除的url
        @param min_block_number: 最小block
        @param times:
        @return:
        """
        logger.info(f'Chain[{self.Name}]Refreshing rpc {f",get rid of {url}" if url else ""}')
        white = set()
        test_rpc_dict = {}
        if url in self.AliveRpcs:
            self.AliveRpcs.remove(url)
        for rpc in self.AllRpcs:
            try:
                web3 = Web3(Web3.HTTPProvider(rpc))
                if geth_poa:
                    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                if local_filter:
                    web3.middleware_onion.add(local_filter_middleware)
                block_number = web3.eth.getBlock('latest').number
                test_rpc_dict[rpc] = block_number
            except Exception as e:
                logger.warning(f'Chain[{self.Name}]<refresh_rpc>Error: {e}')
                if rpc in self.AliveRpcs:
                    self.AliveRpcs.remove(rpc)
                    logger.warning(f'Chain[{self.Name}]<refresh_rpc>Remove rpc:{rpc}')
        if len(test_rpc_dict.values()) > 0:
            max_block_number = max(test_rpc_dict.values())
            if min_block_number:
                for rpc, block_number in test_rpc_dict.items():
                    if max_block_number - block_number < 5 and block_number > min_block_number:
                        white.add(rpc)
            else:
                for rpc, block_number in test_rpc_dict.items():
                    if max_block_number - block_number < 5:
                        white.add(rpc)
            white = self.AliveRpcs & white
            if white:
                self.AliveRpcs = white
                logger.info(f'Chain[{self.Name}]<refresh_rpc> succeeded.')
                return
        else:
            logger.warning(f'Chain[{self.Name}]<refresh_rpc>AliveRpcs is zero, reset white.')
        if times:
            times = times - 1
        else:
            logger.error(f'Chain[{self.Name}]<refresh_rpc>AliveRpcs reset failed, re reset after 60 seconds ..')
            time.sleep(60)
            times = 5
        self.AliveRpcs = copy.deepcopy(self.AllRpcs)
        self.refresh_rpc(geth_poa=geth_poa, local_filter=local_filter, min_block_number=min_block_number, times=times)


    def get_batch_events(self, address, topic, from_block, to_block='latest'):
        web3 = self.get_web3()
        if to_block=="latest":
            to_block = self.get_block_number()
        

        logger.info(f"get_batch_events(): from block { from_block } => { to_block }")
        queries = []
        queries.append({
            "jsonrpc": "2.0",
            "method": "eth_getLogs",
            "params": [
                {
                    "fromBlock": Web3.toHex(from_block),
                    "toBlock": Web3.toHex(to_block),
                    "address": address,
                    "topics": topic,
                }
                ],
            "id": 0,
        })
               
        uri = web3.manager.provider.endpoint_uri
        encoded = FriendlyJsonSerde().json_encode(queries)
        raw_response = make_post_request(uri, to_bytes(text=encoded))
        text_response = to_text(raw_response)
        response = FriendlyJsonSerde().json_decode(text_response)
        if len(response) > 0 and response[0].get('error', None):
            raise Exception(response[0]['error'].get('message'))
        return response[0]['result']

        

@single_chain
class Chain(_Chain):
    pass


class _Address:
    Lower: str
    EIP55: ChecksumAddress

    def __init__(self, address):
        self.Lower = address.lower()
        self.EIP55 = Web3.toChecksumAddress(address)

    def __repr__(self):
        return self.Lower

    @classmethod
    def check(cls, address):
        if isinstance(address, cls):
            return address
        else:
            return cls(address)


@single_address
class Address(_Address):
    pass


@single_abi
class Abi:
    Version: str
    Name: str
    Info: list
    Events: dict

    def __init__(self, abi_dir: str, abi: str):
        self.Version = abi_dir
        self.Name = abi
        abi_path = os.path.join(ABIS_PATH, abi_dir, f'{abi}.json')
        with open(abi_path) as file:
            abi = json.load(file)
        self.Info = abi
        self.Events = self.get_event_names_from_abi()

    def analysis_abi(self) -> dict:
        functions = []
        views = []
        events = []
        constructor = []
        for row in self.Info:
            if row.get('type') == 'event':
                events.append(row)
            elif row.get("stateMutability") == "view":
                views.append(row)
            elif row.get('type') == 'function':
                functions.append(row)
            elif row.get('type') == 'constructor':
                constructor.append(row)
            else:
                logger.purple(f'Unknow in abi: {row}')
        return {'events': events, 'views': views, 'functions': functions, 'constructor': constructor}

    def get_event_names_from_abi(self) -> dict:
        return {row['name']: {event['name']: event['type'] for event in row['inputs']} for row in
                self.analysis_abi()['events']}


class NetWork:
    Chain: Chain
    Abis: dict
    AbiDir: str

    def __init__(self, chain: str, abi_dir, thread_of_refresh_rpc=True):
        self.Chain = Chain(chain, thread_of_refresh_rpc=thread_of_refresh_rpc)
        self.Contracts = {}
        self.Abis = {}
        self.AbiDir = abi_dir

    def refresh_rpc(self, url: str = None, min_block_number: int = None):
        """
        刷新rpc
        @param url: 需剔除的rpc
        @param min_block_number: 最小block_number,小于过滤
        @return:
        """
        self.Chain.refresh_rpc(url=url, min_block_number=min_block_number)

    def get_abi(self, abi_name: str):
        """
        获取ABI
        @param abi_name: ABI名称
        @return: abi list
        """
        if abi_name in self.Abis:
            return self.Abis[abi_name]
        else:
            abi = Abi(self.AbiDir, abi_name)
            self.Abis[abi_name] = abi
            return abi

    @error_retrying
    def get_contract(self, address, abi):
        """
        获取合同
        @param address: 0x..
        @param abi: abi
        @return: 合同
        """
        address = _Address.check(address)
        web3 = self.Chain.get_web3()
        abi = self.get_abi(abi)
        contract = web3.eth.contract(address=address.EIP55, abi=abi.Info)
        self.Contracts[address.Lower] = contract
        return contract

    # event-------------------------------------------------------------------------------------------------------------

    @error_retrying
    def get_events(self, address, abi, eventname, from_block, to_block, argument_filters=None, period=5000, threads=10):
        """
        获取event
        @param address: 0x..
        @param abi: ABI
        @param eventname:
        @param from_block:
        @param to_block:
        @param argument_filters:
        @param period:
        @param threads:
        @return:
        """
        if from_block > to_block:
            return []
        contract = self.get_contract(address, abi)
        periods = [(from_block + i * period, min(from_block + (i + 1) * period - 1, to_block)) for i in
                   range((to_block - from_block) // period + 1)]
        if len(periods) == 1:
            eventfilter = contract.events[eventname].createFilter(fromBlock=from_block, toBlock=to_block,
                                                                  argument_filters=argument_filters)
            events = eventfilter.get_all_entries()
        else:
            pool = mpp.ThreadPool(threads)

            def query(n1, n2):
                event_filter = contract.events[eventname].createFilter(fromBlock=n1, toBlock=n2,
                                                                       argument_filters=argument_filters)
                return event_filter.get_all_entries()

            events = pool.starmap(query, periods)
            events = [a for b in events for a in b]
        return events

    def get_events_generator(self, address, abi, eventname, from_block, to_block, once=50000, threads=10):
        """
        迭代器，用于分批生成event
        @param address:
        @param abi:
        @param eventname:
        @param from_block:
        @param to_block:
        @param once:
        @param threads:
        @return:
        """
        if from_block > to_block:
            return []
        period = int(once / threads)
        for _from in range(from_block, to_block + 1, once):
            _to = _from + once - 1
            _to = _to if _to < to_block else to_block
            events = self.get_events(address, abi, eventname, _from, _to, period=period, threads=threads)
            yield _from, _to, events

    # view -------------------------------------------------------------------------------------------------------------

    def _call(self, fun):
        """
        执行函数(仅在执行步骤重试)
        @param fun:
        @return:
        """
        return fun.call()

    @error_retrying
    def call(self, address: Address, abi, function_name, params=None):
        """
        执行函数(原始返回)
        @param address: 0x..
        @param abi:
        @param function_name: 函数名称
        @param params: 参数
        @return:
        """
        contract = self.get_contract(address.EIP55, abi)
        if params is None:
            params = []
        fun = contract.get_function_by_name(function_name)(*params)
        return self._call(fun)

    @error_retrying
    def execute(self, address, abi, function_name, params=None) -> dict:
        """
        执行函数(返回字典)
        @param address: 0x..
        @param abi:
        @param function_name: 函数名称
        @param params: 参数
        @return:
        """
        contract = self.get_contract(address, abi)
        if params is None:
            params = []
        fun = contract.get_function_by_name(function_name)(*params)
        res = self._call(fun)
        if len(fun.abi['outputs']) == 1:
            return self.format_output(fun.abi['outputs'], [res])
        else:
            return self.format_output(fun.abi['outputs'], res)

    def format_output(self, abi_output: iter, data) -> dict:
        """
        格式化output, 原始2字典
        @param abi_output:
        @param data:
        @return:{...}
        """
        result = {}
        for key, value in zip(abi_output, data):
            if key['type'] == 'tuple':
                result[key['name']] = self.format_output(key['components'], value)
            elif key['type'] == 'tuple[]':
                result[key['name']] = [self.format_output(key['components'], row) for row in value]
            else:
                result[key['name']] = value
        return result

    def multicall(self, details, threads=10):
        """
        @param details:[(network, address, abi, functionName, params)...]
        @param threads:
        @return:
        """
        pool = mpp.ThreadPool(threads)
        return pool.starmap(self.call, details)

    def batch_call(self, address, abi, function_name, struct_list):
        """
        @param address:
        @param abi:
        @param function_name:
        @param struct_list:
        @return:
        """
        if not struct_list:
            return []
        details = [(address, abi, function_name, i) for i in struct_list]
        values = self.multicall(details)
        return values

    def multiexecute(self, details, threads=10):
        """
        @param details:
        @param threads:
        @return:
        """
        pool = mpp.ThreadPool(threads)
        return pool.starmap(self.execute, details)

    def batch_execute(self, address, abi, function_name, struct_list):
        """
        @param address:
        @param abi:
        @param function_name:
        @param struct_list:
        @return:
        """
        if not struct_list:
            return []
        details = [(address, abi, function_name, i) for i in struct_list]
        values = self.multiexecute(details)
        return values

    # transact ---------------------------------------------------------------------------------------------------------

    def transact(self, address, abi, function_name, params, account, private, gas=None, gas_price=None):
        """
        进行交易
        @param address:
        @param abi:
        @param function_name:
        @param params:
        @param account:
        @param private:
        @param gas: 6000000
        @param gas_price: 22000000000
        @return:
        """
        contract = self.get_contract(address, abi)
        nonce = contract.web3.eth.getTransactionCount(account)
        gas = gas or contract.get_function_by_name(function_name)(*params).estimateGas({'from': account}) * 3
        transaction_info = {
            'nonce': nonce,
            'from': account,
            'gas': gas,
            'gasPrice': gas_price
        }
        if not gas_price:
            w = self.Chain.get_web3()
            transaction_info.update({'gasPrice': w.eth.gasPrice})
        tx = contract.get_function_by_name(function_name)(*params).buildTransaction(transaction_info)
        signed_tx = contract.web3.eth.account.signTransaction(tx, private)
        tx_hash = contract.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        receipt = contract.web3.eth.waitForTransactionReceipt(tx_hash)
        return receipt

    def batch_transact(self, address, abi, function_name, struct_list, account, private, gas=6000000,
                       gas_price=22000000000, batch=100):
        """
        # 历史函数，未更正开发
        @param address:
        @param abi:
        @param function_name:
        @param struct_list:
        @param account:
        @param private:
        @param gas:
        @param gas_price:
        @param batch:
        @return:
        """
        receipts = []
        batchs = (len(struct_list) - 1) // batch + 1
        for i in range(batchs):
            for n in range(3):
                try:
                    receipt = self.transact(address, abi, function_name,
                                            [struct_list[i * batch:(i + 1) * batch]],
                                            account, private, gas=gas, gas_price=gas_price)
                    if receipt.status:
                        receipts.append(receipt)
                        logger.info(
                            f'Database batch transaction {i + 1}/{batchs}: ({receipt.transactionHash.hex()}, \
                                {receipt.status})')
                        break
                    else:
                        logger.info(
                            f'Database batch transaction {i + 1}/{batchs}: ({receipt.transactionHash.hex()}, \
                                {receipt.status})')
                except Exception as e:
                    logger.error(f'Rpcs[{self.Chain.Name}]<batch_transact>{e}')
                    logger.error(f'Database batch transaction {i + 1}/{batchs}: {traceback.format_exc()}')
                time.sleep(5)
        return receipts



