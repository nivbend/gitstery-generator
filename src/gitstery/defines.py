from pathlib import Path
from datetime import datetime, timedelta

COMMIT_MSG_WIDTH = 100

PACKAGE_DIR = Path(__file__).parent
DATA_DIR = PACKAGE_DIR / 'data'
assert DATA_DIR.is_dir()

DATE_START = datetime(2019, 1, 1, 0, 0)
DATE_END = datetime(2019, 12, 31, 23, 59)
DATE_MURDER = datetime(2019, 7, 14, 18, 13)
MURDER_DAY = DATE_MURDER.replace(hour=0, minute=0)
DATE_REPORT = datetime(2019, 7, 24, 21, 44)
DATE_REPORT_WEEK_START = DATE_REPORT.replace(hour=0, minute=0) \
    - timedelta(days=DATE_REPORT.weekday())
DATE_REPORT_WEEK_END = DATE_REPORT_WEEK_START + timedelta(days=6)

POLICE_BRANCH = 'gtpd-archive'
ACCESS_POINT_OF_INTEREST = 'BACKDOOR_332'
