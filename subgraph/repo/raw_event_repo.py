from web3 import Web3
from libs.logger import get_logger
from libs.db_mysql import check_tables
from libs.db_mysql import db_session as Session
from .base_repo import BaseRepository

logger = get_logger(__name__)


class RawEventRepo(BaseRepository):
    __database_name = "chain"
    __table_name = "event"
    __create_sql = f"""
        CREATE TABLE {__table_name}
        (
            id                  int primary key auto_increment comment '自增主键',
            block_hash          VARCHAR(66) NOT NULL,
            block_number        INT(20) NOT NULL,
            block_time          INT(64) NOT NULL,
            contract_address    VARCHAR(42) NOT NULL,
            tx_hash             VARCHAR(66) NOT NULL,
            tx_index            INT(11) NOT NULL,
            log_index           INT(11) NOT NULL,
            topic0              VARCHAR(66),
            topic1              VARCHAR(66),
            topic2              VARCHAR(66),
            topic3              VARCHAR(66),
            data                VARCHAR(770)
        );
    """


    def check_table(self):
        tables = {self.__table_name: self.__create_sql}
        check_tables(self.session, self.__database_name, tables)

            
    def create(self, **kwargs):
        sql = f"""
            insert into {self.__table_name}
            (
                block_hash, block_number, block_time, contract_address,
                tx_hash, tx_index, log_index, topic0,
                topic1, topic2, topic3, data
            )
            values
            (
                '{kwargs['block_hash']}', '{kwargs['block_number']}', '{kwargs['block_time']}', '{kwargs['contract_address']}',
                '{kwargs['tx_hash']}', '{kwargs['tx_index']}', '{kwargs['log_index']}', '{kwargs['topic0']}', 
                '{kwargs['topic1']}', '{kwargs['topic2']}', '{kwargs['topic3']}', '{kwargs['data']}'
            );
            """
        self.session.execute(sql)
                


    def update(self):
        pass

    def create_if_not_exist(self, **kwargs):
        tx_hash = kwargs['tx_hash']
        log_index = kwargs['log_index']
        res = self.find_by_tx_hash_log_index(tx_hash, log_index)
        if not res:
            self.create(**kwargs)
        else:
            logger.info(f"{self.name}.create_if_exist(): tx_hash {tx_hash} exist")


    def find_all(self):
        sql = f"""
               select * from {self.__table_name};
            """
        self.session.execute(sql)
        res = self.session.get_dicts()
        return res
        

    def find_by_tx_hash_log_index(self, tx_hash, log_index):
        sql = f"""
            select * from {self.__table_name} 
            where tx_hash='{tx_hash}' and log_index={log_index}
            ;
        """
        self.session.execute(sql)
        res = self.session.get_dicts()
        return res

