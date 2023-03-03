import os
import sys
from .constant import *
from .chains import *
from .path import *
from .test import *


PROCESS_NAME = sys.argv[0].split("/")[-1]
SERVICE_NAME = PROCESS_NAME.split(".")[0].lower()


if len(sys.argv) > 1:
    arg = sys.argv[1].lower()
    if 'test' in arg:
        MODE = "test"
        exec(f'from .test import *')
        print("run test mode...")
        DEBUG = False
        USDT_ADDRESS = "0x05111E862280c8b135bCB5Ee173c557f3e1BBcD8"
    if 'prod' in arg:
        MODE = "prod"
        exec(f'from .prod import *')
        print("run prod mode...")
        DEBUG = False
        USDT_ADDRESS = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"

    if 'jupyter' in sys.argv[-1].lower():
        MODE = "test"
        exec(f'from .test import *')
        print("run test mode...")
        DEBUG = False
        USDT_ADDRESS = "0x05111E862280c8b135bCB5Ee173c557f3e1BBcD8"

from .events import *
