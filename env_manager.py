import json
from pathlib import Path
from typing import Dict, List

from dotenv import dotenv_values, load_dotenv, set_key, unset_key

from config import BASE_DIR, DATA_ROOT, logger

ENV_PATH = BASE_DIR / '.env'
USERS_FILE = DATA_ROOT / 'users.json'
DEFAULT_KEYS = [
    'PROFILE_NAME',
    'APP_ID',
    'APP_SECRET',
    'ACCESS_TOKEN',
    'AD_ACCOUNT_ID',
    'AVERAGE_PRODUCT_VALUE',
    'FB_API_VERSION'
]


def load_env_values() -> Dict[str, str]:
    if not ENV_PATH.exists():
        return {}
    return {key: value for key, value in dotenv_values(ENV_PATH).items() if key and value is not None}


def save_env_values(values: Dict[str, str]) -> None:
    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENV_PATH.touch(exist_ok=True)
    try:
        for key, value in values.items():
            set_key(str(ENV_PATH), key, str(value or ''))
        load_dotenv(dotenv_path=str(ENV_PATH), override=True)
        logger.info('Guardado .env con valores: %s', ', '.join(values.keys()))
    except Exception as exc:
        logger.error('Error guardando .env: %s', exc)


def delete_env_keys(keys: List[str]) -> None:
    if not ENV_PATH.exists():
        return
    try:
        for key in keys:
            unset_key(str(ENV_PATH), key)
        load_dotenv(dotenv_path=str(ENV_PATH), override=True)
        logger.info('Eliminadas llaves de .env: %s', ', '.join(keys))
    except Exception as exc:
        logger.error('Error eliminando llaves de .env: %s', exc)


def load_profiles() -> List[Dict[str, str]]:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        return []
    try:
        with USERS_FILE.open('r', encoding='utf-8') as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        logger.warning('No se pudo leer USERS_FILE, archivo corrupto o vacío: %s', USERS_FILE)
    except Exception as exc:
        logger.error('Error cargando perfiles: %s', exc)
    return []


def save_profile(profile: Dict[str, str]) -> None:
    profiles = load_profiles()
    name = profile.get('PROFILE_NAME', 'default') or 'default'
    profile['PROFILE_NAME'] = name
    profiles = [p for p in profiles if p.get('PROFILE_NAME') != name]
    profiles.append(profile)
    with USERS_FILE.open('w', encoding='utf-8') as handle:
        json.dump(profiles, handle, indent=2, ensure_ascii=False)
    logger.info('Perfil guardado: %s', name)


def delete_profile(name: str) -> None:
    profiles = load_profiles()
    profiles = [p for p in profiles if p.get('PROFILE_NAME') != name]
    with USERS_FILE.open('w', encoding='utf-8') as handle:
        json.dump(profiles, handle, indent=2, ensure_ascii=False)
    logger.info('Perfil eliminado: %s', name)
