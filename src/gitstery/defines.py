from pathlib import Path
from datetime import datetime

COMMIT_MSG_WIDTH = 100

PACKAGE_DIR = Path(__file__).parent
DATA_DIR = PACKAGE_DIR / 'data'
assert DATA_DIR.is_dir()

DATE_START = datetime(2019, 1, 1, 0, 0)
DATE_END = datetime(2019, 12, 31, 23, 59)
DATE_REPORT = datetime(2019, 7, 24, 21, 44)

POLICE_BRANCH = 'gtpd-archive'
