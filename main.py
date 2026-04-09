from datetime import date, timedelta

from config import validate_env, get_today_str
from facebook_client import FacebookClient
from storage import StorageManager


def run_daily_ingestion(days: int = 30):
    validate_env()
    today = date.today()
    date_from = (today - timedelta(days=days - 1)).isoformat()
    date_to = today.isoformat()
    client = FacebookClient()
    rows = client.get_ads_insights(date_from, date_to, level='adset')
    StorageManager.save_raw(rows, 'adset', get_today_str())
    StorageManager.upsert_master(rows, get_today_str())
    print(f'Ingestión completada: {len(rows)} registros guardados.')


if __name__ == '__main__':
    run_daily_ingestion()
