import os
import strawberry
from libs.logger import get_logger
from libs.utils import timing
from typing import List, Optional
from libs.db_mysql import db_session
from libs.utils import hex_to_address, keccak
from config import EVENT_CONFIG
from subgraph.models import *

logger = get_logger(__name__)
EVENT_TABLE = "event"
<<<<<<< HEAD

=======
>>>>>>> 603b6dedeee5b7713db680da1b4e905e375b3daa

@strawberry.input
class Page():
    start: Optional[int] = None
    limit: Optional[int] = None


@strawberry.input
class TransactionFilter:
    tx_hash: Optional[str] = None


@strawberry.input
class SortBy():
    block_number: Optional[str] = None


def get_page(where: Page):
    res = {}
    default_page = {'start': 0, 'limit': 100}
    for prop in ['start', 'limit']:
        prop_value = getattr(where, prop) if hasattr(where, prop) else None
        if prop_value:
            res[prop] = int(prop_value)
        else:
            res[prop] = default_page[prop]
    if int(res['start']) < 0:
        res['start'] = 0
    return res


def get_sort_by(sort_by: SortBy):
    res = {}
    for prop in ['block_number']:
        prop_value = getattr(sort_by, prop) if hasattr(sort_by, prop) else None
        if prop_value:
            res[prop] = prop_value
    return res


def get_account_filter(where: TransactionFilter):
    res = {}
    for prop in ['tx_hash']:
        prop_value = getattr(where, prop) if hasattr(where, prop) else None
        if prop_value:
            res[prop] = prop_value
    return res


def filter_process(event_sig, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}):
    account_filter = get_account_filter(where)
    page_dict = get_page(page)
    sort_by_dict = get_sort_by(sort_by)

    where_clause, sort_clause, limit_clause = "", "", ""
    if account_filter:
        where_clause = f"where topic0='{event_sig}' and " + ' and '.join(
            [f"{k}='{v}'" for k, v in account_filter.items()])
    else:
        where_clause = f"where topic0='{event_sig}'"
    if sort_by_dict:
        sort_clause = f"order by block_number {sort_by_dict['block_number']}"
    if page_dict:
        limit_clause = f"limit {page_dict['limit']} offset {page_dict['start']}"
    return f"{where_clause} {sort_clause} {limit_clause}"


@strawberry.type
class Query:

    @strawberry.field
    @timing
    def deposit_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> List[
        DepositEventEntity]:
        event_sig = keccak("Deposit(address,address,uint256)")
        clause = filter_process(event_sig, where, page, sort_by)
        with db_session() as session:
            sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
            logger.info(sql)
            session.execute(sql)
            res = session.get_dicts()
            logger.info(res)
            if res:
                return [DepositEvent(event).to_entity() for event in res]
            else:
                return [DepositEventEntity()]

    @strawberry.field
    @timing
<<<<<<< HEAD
    def withd{EVENT_TABLE}(self, where: TransactionFilter = {}, page

    : Page = {}, sort_by: SortBy = {}) -> List[WithdrawEventEntity]:
    event_sig = keccak("Withdraw(address,address,uint256,uint256,uint256)")
    clause = filter_process(event_sig, where, page, sort_by)
    with db_session() as session:
        sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
        logger.info(sql)
        session.execute(sql)
        res = session.get_dicts()
        logger.info(res)
        if res:
            return [WithdrawEvent(event).to_entity() for event in res]
        else:
            return [WithdrawEventEntity]


@strawberry.field
@timing
def create_request_withd{EVENT_TABLE}(self, where: TransactionFilter = {}, page

: Page = {}, sort_by: SortBy = {}) -> List[CreateRequestWithdrawEntity]:
event_sig = keccak("CreateRequestWithdraw(uint256,address,address,bytes)")
clause = filter_process(event_sig, where, page, sort_by)
with db_session() as session:
    sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
    logger.info(sql)
    session.execute(sql)
    res = session.get_dicts()
    logger.info(res)
    if res:
        return [CreateRequestWithdrawEvent(event).to_entity() for event in res]
    else:
        return [CreateRequestWithdrawEntity()]


@strawberry.field
@timing
def execute_withd{EVENT_TABLE}(self, where: TransactionFilter = {}, page

: Page = {}, sort_by: SortBy = {}) -> List[ExecuteWithdrawEntity]:
event_sig = keccak("ExecuteWithdraw(uint256,address,address,bytes)")
clause = filter_process(event_sig, where, page, sort_by)
with db_session() as session:
    sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
    logger.info(sql)
    session.execute(sql)
    res = session.get_dicts()
    logger.info(res)
    if res:
        return [ExecuteWithdrawEvent(event).to_entity() for event in res]
    else:
        return [ExecuteWithdrawEntity()]


@strawberry.field
@timing
def cancel_withd{EVENT_TABLE}(self, where: TransactionFilter = {}, page

: Page = {}, sort_by: SortBy = {}) -> List[CancelWithdrawEntity]:
event_sig = keccak("CancelWithdraw(uint256,address,address,bytes)")
clause = filter_process(event_sig, where, page, sort_by)
with db_session() as session:
    sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
    logger.info(sql)
    session.execute(sql)
    res = session.get_dicts()
    logger.info(res)
    if res:
        return [CancelWithdrawEvent(event).to_entity() for event in res]
    else:
        return [CancelWithdrawEntity()]


@strawberry.field
@timing
def log_balance_change_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> List[
    LogBalanceChangeEntity]:
    event_sig = keccak("LogBalanceChange(address,address,int256)")
    clause = filter_process(event_sig, where, page, sort_by)
    with db_session() as session:
        sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
        logger.info(sql)
        session.execute(sql)
        res = session.get_dicts()
        logger.info(res)
        if res:
            return [LogBalanceChangeEvent(event).to_entity() for event in res]
        else:
            return [LogBalanceChangeEntity()]


@strawberry.field
@timing
def log_position_change_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> List[
    LogPositionChangeEntity]:
    event_sig = keccak("LogPositionChange(address,bytes32,int64,int64,int128)")
    clause = filter_process(event_sig, where, page, sort_by)
    with db_session() as session:
        sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
        logger.info(sql)
        session.execute(sql)
        res = session.get_dicts()
        logger.info(res)
        if res:
            return [LogPositionChangeEvent(event).to_entity() for event in res]
        else:
            return [LogPositionChangeEntity()]


schema = strawberry.Schema(query=Query)
=======
    def withdraw_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> List[
        WithdrawEventEntity]:
        event_sig = keccak("Withdraw(address,address,uint256,uint256,uint256)")
        clause = filter_process(event_sig, where, page, sort_by)
        with db_session() as session:
            sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
            logger.info(sql)
            session.execute(sql)
            res = session.get_dicts()
            logger.info(res)
            if res:
                return [WithdrawEvent(event).to_entity() for event in res]
            else:
                return [WithdrawEventEntity]

    @strawberry.field
    @timing
    def create_request_withdraw_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> \
    List[CreateRequestWithdrawEntity]:
        event_sig = keccak("CreateRequestWithdraw(uint256,address,address,bytes)")
        clause = filter_process(event_sig, where, page, sort_by)
        with db_session() as session:
            sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
            logger.info(sql)
            session.execute(sql)
            res = session.get_dicts()
            logger.info(res)
            if res:
                return [CreateRequestWithdrawEvent(event).to_entity() for event in res]
            else:
                return [CreateRequestWithdrawEntity()]

    @strawberry.field
    @timing
    def execute_withdraw_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> List[
        ExecuteWithdrawEntity]:
        event_sig = keccak("ExecuteWithdraw(uint256,address,address,bytes)")
        clause = filter_process(event_sig, where, page, sort_by)
        with db_session() as session:
            sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
            logger.info(sql)
            session.execute(sql)
            res = session.get_dicts()
            logger.info(res)
            if res:
                return [ExecuteWithdrawEvent(event).to_entity() for event in res]
            else:
                return [ExecuteWithdrawEntity()]

    @strawberry.field
    @timing
    def cancel_withdraw_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> List[
        CancelWithdrawEntity]:
        event_sig = keccak("CancelWithdraw(uint256,address,address,bytes)")
        clause = filter_process(event_sig, where, page, sort_by)
        with db_session() as session:
            sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
            logger.info(sql)
            session.execute(sql)
            res = session.get_dicts()
            logger.info(res)
            if res:
                return [CancelWithdrawEvent(event).to_entity() for event in res]
            else:
                return [CancelWithdrawEntity()]

    @strawberry.field
    @timing
    def log_balance_change_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> List[
        LogBalanceChangeEntity]:
        event_sig = keccak("LogBalanceChange(address,address,int256)")
        clause = filter_process(event_sig, where, page, sort_by)
        with db_session() as session:
            sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
            logger.info(sql)
            session.execute(sql)
            res = session.get_dicts()
            logger.info(res)
            if res:
                return [LogBalanceChangeEvent(event).to_entity() for event in res]
            else:
                return [LogBalanceChangeEntity()]

    @strawberry.field
    @timing
    def log_position_change_event(self, where: TransactionFilter = {}, page: Page = {}, sort_by: SortBy = {}) -> List[
        LogPositionChangeEntity]:
        event_sig = keccak("LogPositionChange(address,bytes32,int64,int64,int128)")
        clause = filter_process(event_sig, where, page, sort_by)
        with db_session() as session:
            sql = f"""
                select * from {EVENT_TABLE} {clause};
            """
            logger.info(sql)
            session.execute(sql)
            res = session.get_dicts()
            logger.info(res)
            if res:
                return [LogPositionChangeEvent(event).to_entity() for event in res]
            else:
                return [LogPositionChangeEntity()]


schema = strawberry.Schema(query=Query)
>>>>>>> 603b6dedeee5b7713db680da1b4e905e375b3daa
