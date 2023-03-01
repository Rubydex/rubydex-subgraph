from .raw_event_repo import RawEventRepo
from .deposit_event_repo import DepositEventRepo
from .withdraw_event_repo import WithdrawEventRepo
from libs.db_mysql import db_session


with db_session() as session:
    RawEventRepo(session).check_table()
    DepositEventRepo(session).check_table()
    WithdrawEventRepo(session).check_table()

