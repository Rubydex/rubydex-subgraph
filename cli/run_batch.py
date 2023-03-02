from config import CHAIN
from subgraph.scanner import BATCH_SCANNER
from libs.logger import get_logger
logger = get_logger(__name__)
logger.info("work start")

BATCH_SCANNER(CHAIN).start()
