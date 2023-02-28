from web3 import Web3
from libs.logger import get_logger
from libs.db_mysql import db_session as Session
from .base_repo import BaseRepository

logger = get_logger(__name__)




class WithdrawEventRepo(BaseRepository):
    __database_name = "dc"
    __table_name = "withdraw"
    __create_sql = """
        create table `withdraw`
        (
            `id`                          int primary key auto_increment comment '自增主键',
            `tx_hash`                     varchar(256)                   not null,
            `block_number`                int                                   not null,
            `block_time`                  int                   not null,
            `token`                       varchar(42)              not null,
            `account`                     varchar(42)              not null,
            `amount`                      varchar(256)                not null,
            `expiry`                      int                not null,
            `nonce`                       int                not null
        );"""
    
    # def __init__(self, session: Session):
    #     super().__init__(session)

    def check_table(self):
        self.session.execute(f'use {self.__database_name};')
        self.session.execute('show tables;')
        exist_tables = set(row[0] for row in self.session.get_tuple())
        if self.__table_name not in exist_tables:
            self.session.execute(self.__create_sql)
            logger.info(f"create table - {self.__table_name}")
        else:
            logger.info(f"table - {self.__table_name} existed")

    def create(self, **kwargs):
        sql = f"""
            insert into {self.__table_name}
            (tx_hash, block_number, block_time, token, account, amount, expiry, nonce) 
            values
            (
                '{kwargs['tx_hash']}', '{kwargs['block_number']}', '{kwargs['block_time']}',
                '{kwargs['token']}', '{kwargs['account']}', '{kwargs['amount']}',
                '{kwargs['expiry']}', '{kwargs['nonce']}'
             );
            """
        logger.info(f"sql {sql}")
        self.session.execute(sql)
                

    def update(self):
        pass

    def create_if_not_exist(self, **kwargs):
        tx_hash = kwargs['tx_hash']
        res = self.find_by_tx_hash(tx_hash)
        if not res:
            self.create(**kwargs)
        else:
            token = kwargs['token']
            account = kwargs['account']
            ammount = kwargs['amount']
            logger.info(f"{self.name}.create_if_exist(): {token} {account} {amount} {tx_hash} exist")


    def find_all(self):
        sql = f"""
               select * from {self.__table_name};
            """
        self.session.execute(sql)
        res = self.session.get_dicts()
        return res
        

    def find_by_tx_hash(self, tx_hash):
        sql = f"""
            select * from {self.__table_name} 
            where tx_hash = '{tx_hash}'
            ;
        """
        self.session.execute(sql)
        res = self.session.get_dicts()
        return res

