import logging
import os
from logging import handlers

from config import LOGS_PATH, SERVICE_NAME, DEBUG, MODE

_log_path = os.path.join(LOGS_PATH, f'{SERVICE_NAME}_{MODE}.log')


def set_logger(log_path: str = _log_path):
    os.makedirs(LOGS_PATH, exist_ok=True)
    streamhandler = logging.StreamHandler()
    timedrotatingfilehandler = handlers.TimedRotatingFileHandler(filename=log_path, when='d', interval=1,
                                                                 encoding='utf-8')
    _handlers = [streamhandler, timedrotatingfilehandler]
    _format = '%(asctime)s %(levelname)s: <%(name)s> %(message)s'  # "-%(module)s"
    logging.basicConfig(format=_format, datefmt='%Y-%m-%d %H:%M:%S %p', level=logging.DEBUG if DEBUG else logging.INFO, handlers=_handlers)


logging._levelToName = {
    logging.CRITICAL: '\033[35mCRITICAL\033[0m',
    logging.ERROR: '\033[31mERROR\033[0m',
    logging.WARNING: '\033[33mWARNING\033[0m',
    logging.INFO: '\033[32mINFO\033[0m',
    logging.DEBUG: '\033[34mDEBUG\033[0m',
    logging.NOTSET: 'NOTSET',
}


class Logger(logging.Logger):

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.isEnabledFor(logging.DEBUG):
            msg = f'\033[34m{str(msg)}\033[0m'
            self._log(logging.DEBUG, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        if self.isEnabledFor(logging.WARNING):
            msg = f'\033[33m{str(msg)}\033[0m'
            self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        if self.isEnabledFor(logging.ERROR):
            msg = f'\033[31m{str(msg)}\033[0m'
            self._log(logging.ERROR, msg, args, **kwargs)

    def light(self, msg, *args, level='INFO', highlight=32, **kwargs):
        """
        Log 'msg % args' with severity `level`.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.`light`("Houston, we have a %s", "major problem", exc_info=1)
        """
        level = logging._nameToLevel[level]
        msg = f'\033[{highlight}m{str(msg)}\033[0m'
        self._log(level, msg, args, **kwargs)


def get_highlight_log(highlight):
    def light(self, msg, *args, **kwargs):
        msg = f'\033[{highlight}m{str(msg)}\033[0m'
        self._log(logging.INFO, msg, args, **kwargs)

    return light


logging.Logger.debug = Logger.debug
logging.Logger.warning = Logger.warning
logging.Logger.error = Logger.error
logging.Logger.light = Logger.light

logging.Logger.black = get_highlight_log(30)
logging.Logger.red = get_highlight_log(31)
logging.Logger.green = get_highlight_log(32)
logging.Logger.yellow = get_highlight_log(33)
logging.Logger.blue = get_highlight_log(34)
logging.Logger.purple = get_highlight_log(35)
logging.Logger.cyan = get_highlight_log(36)
logging.Logger.white = get_highlight_log(37)


def get_logger(name):
    logger = logging.getLogger(name)
    return logger

set_logger(_log_path)