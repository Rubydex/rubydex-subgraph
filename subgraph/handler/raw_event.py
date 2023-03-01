from libs.db_mysql import db_session
from libs.logger import get_logger
from subgraph.repo import RawEventRepo

logger = get_logger(__name__)

def raw_event_handler(event, context):
    with db_session() as session:
        deposit_event_repo = RawEventRepo(session)
        deposit_event_repo.create_if_not_exist(**event)

        
