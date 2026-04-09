import os
from pathlib import Path
from typing import List

import pandas as pd

from config import PROCESSED_DIR, RAW_DIR, logger, get_today_str


def get_storage_path():
    """Ruta para guardar los datos de Facebook Ads"""
    if os.environ.get('RENDER'):
        return '/data/facebook_data'
    else:
        return os.path.join(os.path.dirname(__file__), 'data', 'facebook_data')


class StorageManager:
    @staticmethod
    def save_raw(records: List[dict], level: str, date_str: str) -> Path:
        folder = RAW_DIR / date_str
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f'raw_{level}.parquet'
        df = pd.DataFrame(records)
        df['report_date'] = date_str
        df.to_parquet(path, index=False)
        logger.info('Guardado archivo raw: %s', path)
        return path

    @staticmethod
    def load_master() -> pd.DataFrame:
        path = PROCESSED_DIR / 'ads_master.parquet'
        if path.exists():
            return pd.read_parquet(path)
        return pd.DataFrame()

    @staticmethod
    def upsert_master(records: List[dict], date_str: str) -> Path:
        df = pd.DataFrame(records)
        df['report_date'] = date_str
        if 'adset_id' in df:
            df['level'] = df['adset_id'].apply(lambda x: 'adset' if x else 'campaign')
        else:
            df['level'] = 'campaign'
        if df.empty:
            logger.warning('No hay registros nuevos para upsert en el maestro')
            path = PROCESSED_DIR / 'ads_master.parquet'
            if not path.exists():
                pd.DataFrame().to_parquet(path, index=False)
            return path

        master = StorageManager.load_master()
        key_cols = ['date_start', 'campaign_id', 'adset_id', 'level']

        if not master.empty:
            master = master.drop_duplicates(subset=key_cols, keep='last').set_index(key_cols)
            df = df.drop_duplicates(subset=key_cols, keep='last').set_index(key_cols)
            master.update(df)
            combined = pd.concat([master, df[~df.index.isin(master.index)]])
            combined = combined.reset_index()
        else:
            combined = df.reset_index(drop=True)

        path = PROCESSED_DIR / 'ads_master.parquet'
        combined.to_parquet(path, index=False)
        logger.info('Archivo maestro actualizado: %s filas totales', len(combined))
        return path
