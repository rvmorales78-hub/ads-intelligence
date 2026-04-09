import logging
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path(os.getenv('DATA_ROOT', BASE_DIR / 'data'))
RAW_DIR = DATA_ROOT / 'raw'
PROCESSED_DIR = DATA_ROOT / 'processed'
LOG_FILE = BASE_DIR / 'app.log'
ENV_PATH = BASE_DIR / '.env'

DATA_ROOT.mkdir(parents=True, exist_ok=True)

AVERAGE_PRODUCT_VALUE = float(os.getenv('AVERAGE_PRODUCT_VALUE', '100.0'))
FB_API_VERSION = os.getenv('FB_API_VERSION', 'v20.0')

REQUIRED_ENV_VARS = ['APP_ID', 'ACCESS_TOKEN', 'AD_ACCOUNT_ID']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ads_intelligence')


def validate_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        msg = f'Missing environment variables: {", ".join(missing)}'
        logger.error(msg)
        raise EnvironmentError(msg)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def format_currency(value: float) -> str:
    return f'${value:,.2f}'


def format_ratio(value: float) -> str:
    return f'{value:.2f}'


def get_today_str() -> str:
    return datetime.utcnow().strftime('%Y-%m-%d')
