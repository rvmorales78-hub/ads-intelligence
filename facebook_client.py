import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from facebook_business.api import FacebookAdsApi  # type: ignore[import]
from facebook_business.adobjects.adaccount import AdAccount  # type: ignore[import]
from facebook_business.exceptions import FacebookRequestError  # type: ignore[import]

from config import logger


class FacebookClient:
    def __init__(self):
        self.access_token = os.getenv('ACCESS_TOKEN', '')
        self.app_id = os.getenv('APP_ID', '')
        self.app_secret = os.getenv('APP_SECRET', '')
        self.ad_account_id = os.getenv('AD_ACCOUNT_ID', '')
        self.api_version = os.getenv('FB_API_VERSION', 'v20.0')

        if not self.access_token or not self.app_id or not self.ad_account_id:
            raise ValueError('APP_ID, ACCESS_TOKEN y AD_ACCOUNT_ID deben estar definidos en el entorno')

        normalized_account = self.ad_account_id.strip()
        if normalized_account.startswith('act_'):
            normalized_account = normalized_account[4:]

        if not normalized_account:
            raise ValueError('AD_ACCOUNT_ID no puede estar vacío')

        self.api = FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token, api_version=self.api_version)
        self.account = AdAccount(f'act_{normalized_account}')

    def verify_access_token(self) -> Dict:
        logger.info('Verificando token de acceso...')
        if self.app_secret:
            debug_url = f'https://graph.facebook.com/{self.api_version}/debug_token'
            params = {
                'input_token': self.access_token,
                'access_token': f'{self.app_id}|{self.app_secret}'
            }
            response = requests.get(debug_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json().get('data', {})

            if not data.get('is_valid'):
                message = data.get('error', {}).get('message', 'Token inválido o expirado')
                logger.error(f'Verificación de token falló: {message}')
                raise ValueError(f'Access token is not valid: {message}')

            expires_at = data.get('expires_at')
            if expires_at and expires_at < int(datetime.utcnow().timestamp()):
                logger.error('El token de acceso ha expirado')
                raise ValueError('Access token has expired')

            logger.info('Token válido hasta %s', datetime.utcfromtimestamp(expires_at).isoformat() if expires_at else 'desconocido')
            return data

        me_url = f'https://graph.facebook.com/{self.api_version}/me'
        response = requests.get(me_url, params={'access_token': self.access_token}, timeout=15)
        response.raise_for_status()
        data = response.json()

        if 'id' not in data:
            logger.error('Token inválido o sin permisos: %s', data)
            raise ValueError('Access token is not valid or lacks permissions')

        logger.info('Token válido para usuario %s', data.get('id'))
        return data

    def _retry(self, func, max_attempts=3, initial_backoff=1, **kwargs):
        attempt = 0
        while attempt < max_attempts:
            try:
                return func(**kwargs)
            except (requests.RequestException, FacebookRequestError) as exc:
                wait = initial_backoff * (2 ** attempt)
                attempt += 1
                logger.warning('Intento %s falló: %s. Reintentando en %ss', attempt, exc, wait)
                time.sleep(wait)
        raise RuntimeError('Máximo de reintentos alcanzado para la petición a Meta API')

    def _call_insights(self, fields: List[str], params: Dict) -> Any:
        try:
            return self.account.get_insights(fields=fields, params=params)
        except TypeError:
            # Fallback if SDK does not accept async parameter directly
            return self.account.get_insights(fields=fields, params=params)

    def _fetch_insights(self, fields: List[str], time_range: Dict, level: str, async_mode: bool = False) -> List[Dict]:
        params = {
            'time_range': time_range,
            'time_increment': 1,
            'level': level,
            'limit': 500,
            'breakdowns': []
        }
        if async_mode:
            params['async'] = True

        logger.info('Solicitando insights para nivel=%s, rango=%s', level, time_range)
        insights: Any = self._retry(self._call_insights, fields=fields, params=params)

        if async_mode and isinstance(insights, dict):  # response may be async job object
            if insights.get('async_status') and insights.get('async_status') != 'Job Completed':
                job_id = str(insights.get('report_run_id') or insights.get('async_job_id') or '')
                if not job_id:
                    raise RuntimeError('No se encontró job_id válido en la respuesta async de Facebook')
                return self._poll_async_report(job_id)

        rows = []
        for row in insights:
            rows.append(row)
        logger.info('Recibidos %s registros de insights', len(rows))
        return rows

    def _poll_async_report(self, job_id: str) -> List[Dict]:
        logger.info('Puleando reporte async job_id=%s', job_id)
        status_url = f'https://graph.facebook.com/{self.api_version}/{job_id}'
        while True:
            response = requests.get(status_url, params={'access_token': self.access_token, 'fields': 'async_percent_completion,async_status,result'}).json()
            status = response.get('async_status')
            if status == 'Job Completed':
                logger.info('Reporte async completado')
                return response.get('result', [])
            if status in {'Job Failed', 'Failed'}:
                raise RuntimeError(f'Async report failed: {response}')
            percent = response.get('async_percent_completion', 0)
            logger.info('Reporte pendiente %s%%', percent)
            time.sleep(3)

    def _normalize_actions(self, row: Dict) -> Dict:
        raw_actions = row.get('actions', []) or []
        if isinstance(raw_actions, dict):
            raw_actions = [raw_actions]

        if raw_actions:
            logger.info('RAW ACTIONS: %s', json.dumps(raw_actions, indent=2, ensure_ascii=False))

        actions = {}
        for action in raw_actions:
            if not isinstance(action, dict):
                continue
            action_type = str(action.get('action_type', '') or '').lower()
            value = float(action.get('value', 0) or 0)
            actions[action_type] = actions.get(action_type, 0.0) + value

        raw_values = row.get('action_values', []) or []
        if isinstance(raw_values, dict):
            raw_values = [raw_values]

        if raw_values:
            logger.info('RAW ACTION VALUES: %s', json.dumps(raw_values, indent=2, ensure_ascii=False))

        values = {}
        for value_row in raw_values:
            if not isinstance(value_row, dict):
                continue
            action_type = str(value_row.get('action_type', '') or '').lower()
            value = float(value_row.get('value', 0) or 0)
            values[action_type] = values.get(action_type, 0.0) + value

        purchases = 0
        for action_type, value in actions.items():
            action_lower = action_type.lower()
            if action_lower == 'purchase':
                purchases = int(value)
                break
            if 'purchase' in action_lower:
                purchases = int(value)
            elif action_lower == 'offsite_conversion.fb_pixel_purchase':
                purchases = int(value)
            elif action_lower == 'mobile_app_purchase':
                purchases = int(value)

        logger.info('Purchases encontradas: %s de acciones: %s', purchases, actions)

        purchase_value = 0.0
        for action_type, value in values.items():
            action_lower = action_type.lower()
            if action_lower == 'purchase':
                purchase_value = value
                break
            if 'purchase' in action_lower:
                purchase_value = value

        logger.info('Purchase value detectado: %s de action_values: %s', purchase_value, values)

        return {
            'purchases': purchases,
            'leads': int(actions.get('lead', 0) or actions.get('leadgen', 0) or 0),
            'registrations': int(actions.get('complete_registration', 0) or 0),
            'add_to_cart': int(actions.get('add_to_cart', 0) or 0),
            'purchase_value': float(purchase_value),
            'cost_per_purchase': float(row.get('cost_per_purchase', 0.0) or 0.0),
            'roas_metric': float(row.get('purchase_roas', 0.0) or 0.0)
        }

    def _map_objective(self, objective_code: str) -> str:
        """Mapea código de objetivo a nombre legible en español"""
        objective_map = {
            'APP_INSTALLS': 'Instalaciones de App',
            'BRAND_AWARENESS': 'Reconocimiento',
            'CONVERSIONS': 'Conversiones',
            'EVENT_RESPONSES': 'Eventos',
            'LEAD_GENERATION': 'Generación de Leads',
            'LINK_CLICKS': 'Tráfico',
            'MESSAGES': 'Mensajes',
            'OFFER_CLAIMS': 'Ofertas',
            'OUTCOME_ENGAGEMENT': 'Engagement',
            'OUTCOME_TRAFFIC': 'Tráfico',
            'PAGE_LIKES': 'Likes',
            'POST_ENGAGEMENT': 'Engagement',
            'PRODUCT_CATALOG_SALES': 'Ventas',
            'REACH': 'Alcance',
            'STORE_VISITS': 'Visitas',
            'VIDEO_VIEWS': 'Video',
            'UNKNOWN': 'No especificado'
        }
        return objective_map.get(str(objective_code).upper(), str(objective_code))

    def get_campaigns_with_objectives(self) -> Dict[str, str]:
        """Obtiene el objetivo de cada campaña directamente"""
        try:
            fields = ['id', 'name', 'objective']
            campaigns = self.account.get_campaigns(fields=fields, params={'limit': 500})
            objectives = {}
            for campaign in campaigns:
                campaign_id = str(campaign.get('id'))
                objective = campaign.get('objective', 'UNKNOWN')
                objective_name = self._map_objective(objective)
                objectives[campaign_id] = objective_name
            logger.info(f"Obtenidos objetivos para {len(objectives)} campañas")
            return objectives
        except Exception as exc:
            logger.warning(f"No se pudieron obtener objetivos: {exc}")
            return {}

    def _fetch_campaign_statuses(self) -> Dict[str, Dict[str, str]]:
        try:
            fields = ['id', 'name', 'effective_status', 'configured_status', 'status', 'objective']
            statuses = {}
            campaigns = self.account.get_campaigns(fields=fields, params={'limit': 500})
            for campaign in campaigns: # type: ignore
                campaign_id = str(campaign.get('id'))
                statuses[campaign_id] = {
                    'campaign_name': campaign.get('name', ''),
                    'effective_status': str(campaign.get('effective_status', '') or '').upper(),
                    'configured_status': str(campaign.get('configured_status', '') or '').upper(),
                    'status': str(campaign.get('status', '') or '').upper(),
                    'objective': campaign.get('objective', ''),
                }
            logger.info('Recibidos %s estados de campaña', len(statuses))
            return statuses
        except Exception as exc:
            logger.warning('No se pudo obtener estados de campaña: %s', exc)
            return {}

    def get_campaigns_status(self) -> List[Dict]:
        campaign_statuses = self._fetch_campaign_statuses()
        return [
            {
                'campaign_id': campaign_id,
                'campaign_name': data.get('campaign_name', ''),
                'effective_status': data.get('effective_status', 'UNKNOWN'),
                'configured_status': data.get('configured_status', 'UNKNOWN'),
                'status': data.get('status', 'UNKNOWN'),
                'objective': data.get('objective', 'UNKNOWN'),
            }
            for campaign_id, data in campaign_statuses.items()
        ]

    def _fetch_adset_statuses(self) -> Dict[str, str]:
        try:
            fields = ['id', 'effective_status']
            statuses = {}
            adsets = self.account.get_ad_sets(fields=fields, params={'limit': 500})
            for adset in adsets: # type: ignore
                adset_id = str(adset.get('id'))
                statuses[adset_id] = str(adset.get('effective_status', '') or '').upper()
            logger.info('Recibidos %s estados de adset', len(statuses))
            return statuses
        except Exception as exc:
            logger.warning('No se pudo obtener estados de adset: %s', exc)
            return {}

    def _attach_status_fields(self, rows: List[Dict], level: str) -> List[Dict]:
        campaign_statuses = self._fetch_campaign_statuses()
        adset_statuses = self._fetch_adset_statuses() if level == 'adset' else {}

        for row in rows:
            campaign_id = str(row.get('campaign_id', ''))
            adset_id = str(row.get('adset_id', ''))
            status = ''
            if level == 'campaign':
                status = campaign_statuses.get(campaign_id, row.get('effective_status', ''))
            else:
                status = adset_statuses.get(adset_id, '') or campaign_statuses.get(campaign_id, row.get('effective_status', ''))
            row['status'] = str(status).upper() if status is not None else ''
        return rows

    def get_ads_insights(self, date_from: str, date_to: str, level: str = 'campaign') -> List[Dict]:
        self.verify_access_token()
        start_date = datetime.fromisoformat(date_from)
        end_date = datetime.fromisoformat(date_to)
        days = (end_date - start_date).days + 1
        async_mode = days > 30

        time_range = {'since': date_from, 'until': date_to}
        campaign_objectives = self.get_campaigns_with_objectives()
        delivery_fields = [
            'campaign_name', 'campaign_id', 'adset_name', 'adset_id',
            'date_start', 'date_stop',
            'impressions', 'clicks', 'spend', 'ctr', 'cpc', 'cpm', 'frequency', 'reach',
            'quality_ranking', 'engagement_rate_ranking', 'conversion_rate_ranking',
            'effective_status', 'objective'
        ]
        action_fields = [
            'campaign_name', 'campaign_id', 'adset_name', 'adset_id',
            'date_start', 'date_stop',
            'actions', 'action_values', 'conversions', 'cost_per_action_type',
            'purchase_roas', 'cost_per_purchase',
            'effective_status', 'objective'
        ]

        try:
            delivery_rows = self._fetch_insights(delivery_fields, time_range, level, async_mode=async_mode)
            action_rows = self._fetch_insights(action_fields, time_range, level, async_mode=async_mode)
        except Exception as exc:
            logger.warning('No se pudo obtener effective_status directamente: %s. Reintentando sin campo de estado.', exc)
            delivery_fields = [
                'campaign_name', 'campaign_id', 'adset_name', 'adset_id',
                'date_start', 'date_stop',
                'impressions', 'clicks', 'spend', 'ctr', 'cpc', 'cpm', 'frequency', 'reach',
                'quality_ranking', 'engagement_rate_ranking', 'conversion_rate_ranking',
                'objective'
            ]
            action_fields = [
                'campaign_name', 'campaign_id', 'adset_name', 'adset_id',
                'date_start', 'date_stop',
                'actions', 'action_values', 'purchase_roas', 'cost_per_purchase',
                'objective'
            ]
            delivery_rows = self._fetch_insights(delivery_fields, time_range, level, async_mode=async_mode)
            action_rows = self._fetch_insights(action_fields, time_range, level, async_mode=async_mode)

        logger.info('Fetch completed: delivery_rows=%s action_rows=%s', len(delivery_rows), len(action_rows))
        merged = {}
        for row in delivery_rows:
            campaign_id = row.get('campaign_id', '')
            adset_id = row.get('adset_id', '') or 'campaign_level'  # ← Fix para nivel campaign
            key = (campaign_id, adset_id, row.get('date_start'))
            merged[key] = {
                'campaign_name': row.get('campaign_name', ''),
                'campaign_id': row.get('campaign_id', ''),
                'adset_name': row.get('adset_name', ''),
                'adset_id': row.get('adset_id', ''),
                'date_start': row.get('date_start', ''),
                'date_stop': row.get('date_stop', ''),
                'impressions': int(row.get('impressions', 0) or 0),
                'clicks': int(row.get('clicks', 0) or 0),
                'spend': float(row.get('spend', 0.0) or 0.0),
                'ctr': float(row.get('ctr', 0.0) or 0.0),
                'cpc': float(row.get('cpc', 0.0) or 0.0),
                'cpm': float(row.get('cpm', 0.0) or 0.0),
                'frequency': float(row.get('frequency', 0.0) or 0.0),
                'reach': int(row.get('reach', 0) or 0),
                'quality_ranking': row.get('quality_ranking', ''),
                'engagement_rate_ranking': row.get('engagement_rate_ranking', ''),
                'conversion_rate_ranking': row.get('conversion_rate_ranking', ''),
                'effective_status': row.get('effective_status', ''),
                'objective': row.get('objective', 'UNKNOWN')
            }

        for row in action_rows:
            campaign_id = row.get('campaign_id', '')
            adset_id = row.get('adset_id', '') or 'campaign_level'
            key = (campaign_id, adset_id, row.get('date_start'))
            if key not in merged:
                merged[key] = {
                    'campaign_name': row.get('campaign_name', ''),
                    'campaign_id': row.get('campaign_id', ''),
                    'adset_name': row.get('adset_name', ''),
                    'adset_id': row.get('adset_id', ''),
                    'date_start': row.get('date_start', ''),
                    'date_stop': row.get('date_stop', ''),
                    'impressions': 0,
                    'clicks': 0,
                    'spend': 0.0,
                    'ctr': 0.0,
                    'cpc': 0.0,
                    'cpm': 0.0,
                    'frequency': 0.0,
                    'reach': 0,
                    'quality_ranking': '',
                    'engagement_rate_ranking': '',
                    'conversion_rate_ranking': '',
                    'effective_status': row.get('effective_status', ''),
                'objective': row.get('objective', 'UNKNOWN')
                }
            merged[key].update(self._normalize_actions(row))

        result = list(merged.values())
        result = self._attach_status_fields(result, level)

        for row in result:
            campaign_id = str(row.get('campaign_id', ''))
            row['objective'] = campaign_objectives.get(campaign_id, 'No especificado')

        return result
