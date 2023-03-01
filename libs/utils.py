import numpy as np
import time
from web3 import Web3
from decimal import Decimal
from functools import wraps
# def format_decimals(val):
#     return int(val * 1E18)

def format_decimals(val: Decimal):
    return int(val * int(1E18))

def hex_to_address(val):
    return Web3.toChecksumAddress(val[-40:])

def keccak(data):
    return Web3.keccak(text=data).hex()

def padding(hexstr, padding=16):
    valid_len = len(hexstr[2:])
    if padding - valid_len >= 0:
        return '0' * (padding - valid_len) + hexstr[2:]


def dec_to_hex(dec_interger, width=64):
    two_comp_binary = np.binary_repr(dec_interger, width=width)
    hex_val = hex(int(two_comp_binary, 2))
    return padding(hex_val, padding=width // 4)


def timing(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time.time()
        result = f(*args, **kwargs)
        te = time.time()
        print(f"--- timing: {f.__name__}, args:[{args if args else ''}, {kwargs}], took: {te-ts:2.3f}s ")
        return result
    return wrap

def retry_with_web3(times, exceptions):
    def decorator(func):
        @wraps(func)
        def new_fn(*args, **kw_args):
            # todo: need to specify args using kwargs feature
            if len(args) > 0:
                # web3 call
                if isinstance(args[0], Web3):
                    w3 = args[0]
                # contract call
                elif isinstance(args[0], list):
                    if isinstance(args[0][0], Contract):
                        contract = args[0][0]
                    # for event registry
                    elif isinstance(args[0][0], tuple) and isinstance(args[0][0][0], Contract):
                        contract = args[0][0][0]
                elif isinstance(args[0], Contract):
                    contract = args[0]
                else:
                    contract = None
            else:
                contract = None

            if 'contract' in locals():
                w3 = contract.w3
            elif not 'w3' in locals():
                w3 = None

            attempt = 0
            timeout_retry_times = 10
            while attempt < times:
                try:
                    return func(*args, **kw_args)
                # except exceptions:
                except (TypeError, ABIFunctionNotFound) as ex:
                    raise ex
                except BadFunctionCallOutput as ex:
                    # log error at last retry
                    if attempt == times - 1:
                        logger.warn(f"-- {ex}")
                except ReadTimeout as ex:
                    logger.warn(f"-- {ex}")
                    timeout_retry_times -= 1
                    if timeout_retry_times == 0:
                        attempt = times
                    else:
                        time.sleep(0.6)
                        continue
                except Exception as ex:
                    # traceback.print_exc()
                    # logger.error(f"-- {type(ex)} {ex}")
                    # if attempt == times - 1:
                    logger.error(f"{type(ex)} {ex}, run {func.__name__}({args, kw_args}), attempt {attempt} of {times}")
                    # refresh web3
                    if w3:
                        w3 = w3.refresh()
                        if 'contract' in locals():
                            contract.w3 = w3
                attempt += 1
                time.sleep(1 * (attempt + 1))
            # refresh web3 at last
            if w3:
                w3 = w3.refresh()
                if 'contract' in locals():
                    contract.w3 = w3
            return func(*args, **kw_args)
        return new_fn
    return decorator


def get_object(object_instance, selected):
    object_datas = []
    for object_data_name in dir(object_instance):
        if hasattr(object_instance, object_data_name):
            object_datas.append(
                {object_data_name: getattr(object_instance, object_data_name)})
    for d in object_datas:
        if selected in d:
            return d[selected]