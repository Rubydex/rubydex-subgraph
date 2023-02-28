import time
from datetime import datetime
from contextlib import contextmanager
import pymysql
from pymysql.constants import CLIENT
from pymysql.err import IntegrityError
from config import MYSQL_INFORMATION
from .logger import get_logger

logger = get_logger(__name__)

int2type = {0: 'DECIMAL', 1: 'TINY', 2: 'SHORT', 3: 'LONG', 4: 'FLOAT', 5: 'DOUBLE', 6: 'NULL', 7: 'TIMESTAMP',
            8: 'LONGLONG', 9: 'INT24', 10: 'DATE', 11: 'TIME', 12: 'DATETIME', 13: 'YEAR', 14: 'NEWDATE', 15: 'VARCHAR',
            16: 'BIT', 245: 'JSON', 246: 'NEWDECIMAL', 247: 'ENUM', 248: 'SET', 249: 'TINY_BLOB', 250: 'MEDIUM_BLOB',
            251: 'LONG_BLOB', 252: 'BLOB', 253: 'VAR_STRING', 254: 'STRING', 255: 'GEOMETRY'}

need_quotation = [10, 11, 12, 15, 16, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255]


class MysqlLink:
    def __init__(self, mysql_information: dict):
        mysql_information.update({'client_flag': CLIENT.MULTI_STATEMENTS})
        self.connect = pymysql.connect(**mysql_information)
        self.cursor = self.connect.cursor()

    def test(self, _sql: str):
        sql = f'select * from ({_sql}) _sql limit 1;'
        try:
            self.cursor.execute(sql)
        except pymysql.err.ProgrammingError as e:
            logger.purple(_sql)
            logger.purple(e)
            return False
        return True

    def execute(self, _sql: str, insert_count: int = 3):
        """
        检查连接是否断开，如果断开就进行重连
        @param _sql:
        @param insert_count: 执行失败后，重新执行次数
        @return:是否执行成功
        """
        try:
            self.connect.ping(reconnect=True)
            self.cursor.execute(_sql)
            self.connect.commit()  # 提交事务
        except IntegrityError as e:
            logger.warning(f'[IntegrityError:existed]{e}')
        except pymysql.err.ProgrammingError as e:
            logger.purple(_sql)
            raise e
        except pymysql.err.OperationalError as e:
            logger.purple(f'[Exception]{e}')
            self.connect.rollback()  # 回滚
            if insert_count > 0:
                insert_count = insert_count - 1
                time.sleep(10)
                return self.execute(_sql, insert_count=insert_count)
            else:
                _sql = _sql.replace('\n', ' ')
                logger.error(f'[sql]{_sql}')
                return False
        except Exception as e:
            logger.purple(_sql)
            logger.purple(f'[Exception]{e}')
            raise e
        return True

    # 获取结果
    def get_tuple(self) -> tuple:
        """
        @return: ((),(),...)
        """
        res = self.cursor.fetchall()
        return res

    def get_list(self, datetime2str=False) -> list:
        """
        @datetime2str: datetime是否转换
        @return: [[],[],...]
        """
        rows = self.cursor.fetchall()
        res = [[value if not datetime2str and not isinstance(value, datetime) else str(value) for value in row]
               for row in rows]
        return res

    def get_dicts(self, datetime2str=False) -> list:
        """
        @datetime2str: datetime是否转换
        @return: [{},{},...]
        """
        fields = self.cursor.description
        rows = self.cursor.fetchall()
        res = [{fields[field][0]: value if not datetime2str and not isinstance(field, datetime) else str(value)
                for field, value in enumerate(row)} for row in rows]
        return res

    def get_dict_by_field(self, _field: str, datetime2str=False) -> dict:
        """
        @param _field: 字段名
        @param datetime2str: datetime是否转换
        @return:
        """
        if not self.cursor.description:
            return {}
        fields = [row[0] for row in self.cursor.description]
        if _field not in fields:
            raise Exception('Field not found.')
        row_list = self.get_dicts(datetime2str=datetime2str)
        res = {row[_field]: row for row in row_list}
        return res

    def get_fields(self) -> list:
        """
        @return: [...]
        """
        fields_info = self.cursor.description
        res = [row[0] if isinstance(row, tuple) else row for row in fields_info]
        return res

    def get_fields2type(self) -> dict:
        """
        @return: [...]
        """
        fields_info = self.cursor.description
        res = {row[0]: row[1] for row in fields_info}
        return res

    def execute_sqls(self, _sql: str):
        """
        执行多个sql
        @param _sql:
        @return:
        """
        try:
            self.connect.ping(reconnect=True)
            self.cursor.execute(_sql)
            self.connect.commit()
        except Exception as e:  # 发生错误，二分法快速执行
            logger.error(f'{e}')
            self.connect.rollback()
            sqls = _sql.split(';')
            count = len(sqls)
            if count > 3:
                half = count // 2
                sql_1 = sqls[0:half]
                sql_2 = sqls[half:]
                sql_1 = ';'.join(sql_1)
                sql_2 = ';'.join(sql_2)
                self.execute_sqls(sql_1)
                self.execute_sqls(sql_2)
            elif count == 3:
                self.execute(sqls[0])
                self.execute(sqls[1])
                self.execute(sqls[2])
            elif count == 2:
                self.execute(sqls[0])
                self.execute(sqls[1])

    def close(self):
        self.connect.close()


def format_sql(_sql):
    sql = _sql.replace('\n', ' ').strip()
    if sql[-1] == ';':
        sql = sql[:-1]
    return sql


def get_db(parameter=MYSQL_INFORMATION):
    return MysqlLink(parameter)


def check_databases(db: MysqlLink, databases: set):
    """
    检查库
    @param db: MysqlLink
    @param databases: 库名
    @return:
    """
    db.execute('show databases;')
    s = db.get_tuple()
    exist_databases = set(row[0] for row in s)
    for database in databases:
        logger.info(f'Checking database {database}...')
        if database not in exist_databases:
            logger.info(f'Database {database} is not created, creating...')
            db.execute(f"create database `{database}`;")
            logger.info(f'Database {database} has created.')
        else:
            logger.info(f'Database {database} is created.')


def check_tables(db: MysqlLink, database: str, tables: dict):
    """
    检查表
    @param db: MysqlLink
    @param database: 表所在库
    @param tables: 表名
    @return:
    """
    db.execute(f'use {database};')
    db.execute('show tables;')
    exist_tables = set(row[0] for row in db.get_tuple())
    for table, create_sql in tables.items():
        if table not in exist_tables:
            db.execute(create_sql)

def check_table_exist(db: MysqlLink, database: str, table: str):
    """
    检查表
    @param db: MysqlLink
    @param database: 表所在库
    @param tables: 表名
    @return:
    """
    db.execute(f'use {database};')
    db.execute('show tables;')
    exist_tables = set(row[0] for row in db.get_tuple())
    if table in exist_tables:
        return True
    else:
        return False


@contextmanager
def db_session():
    db = get_db()
    try:
        yield db
    # except Exception as ex:
    #     logger.error(f"db_session error: {ex}")
    finally:
        db.connect.close()