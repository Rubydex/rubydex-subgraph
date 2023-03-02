from .raw_event_repo import RawEventRepo
from libs.db_mysql import db_session


with db_session() as session:
    RawEventRepo(session).check_table()

