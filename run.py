from subgraph.scanner import WS_SCANNER
from libs.logger import get_logger
logger = get_logger(__name__)
logger.info("work start")

WS_SCANNER("arbitrumtestnet").start()
