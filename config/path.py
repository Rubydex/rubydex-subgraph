import os

__all__ = [
    'LOCAL_PATH',
    'MAIN_PATH',
    'VENV_PATH',
    'SCRIPTS_PATH',
    'LOGS_PATH',
    'RECORD_PATH',
    'PYTHON_PATH_OF_LINUX',
    'PYTHON_PATH_OF_WINDOWS',
    'GUNICORN_PATH_OF_LINUX',
    'GUNICORN_PATH_OF_WINDOWS',
    'ABIS_PATH',
]

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
MAIN_PATH = os.path.dirname(LOCAL_PATH)
VENV_PATH = os.path.join(MAIN_PATH, '.venv')
SCRIPTS_PATH = os.path.join(MAIN_PATH, 'scripts')

LOGS_PATH = os.path.join(MAIN_PATH, 'Logs')
RECORD_PATH = os.path.join(MAIN_PATH, 'Record')

PYTHON_PATH_OF_LINUX = os.path.join(VENV_PATH, 'bin', 'python')
PYTHON_PATH_OF_WINDOWS = os.path.join(VENV_PATH, 'Scripts', 'python.exe')

GUNICORN_PATH_OF_LINUX = os.path.join(VENV_PATH, 'bin', 'gunicorn')
GUNICORN_PATH_OF_WINDOWS = os.path.join(VENV_PATH, 'Lib', 'gunicorn')

ABIS_PATH = os.path.join(MAIN_PATH, 'abis')

