#!/usr/bin/env python
"""Script temporal para depurar qué devuelve la API de Facebook."""

import json
import logging
from facebook_client import FacebookClient

# Configurar logging para ver los mensajes INFO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    print("Iniciando prueba de conexión a Facebook API...")

    client = FacebookClient()

    # Probar con los últimos 7 días
    date_from = "2026-03-30"
    date_to = "2026-04-07"

    print(f"📅 Consultando insights desde {date_from} hasta {date_to}...")

    try:
        insights = client.get_ads_insights(date_from, date_to, level='campaign')

        print(f"\nTotal de filas obtenidas: {len(insights)}")

        print("\n📊 Detalle de las primeras campañas:")
        print("-" * 80)

        for i, row in enumerate(insights[:5]):
            print(f"\n{i+1}. Campaña: {row.get('campaign_name', 'N/A')}")
            print(f"   Spend: ${float(row.get('spend', 0)):.2f}")
            print(f"   Impressions: {int(row.get('impressions', 0)):,}")
            print(f"   Clicks: {int(row.get('clicks', 0)):,}")
            print(f"   Purchases: {int(row.get('purchases', 0))}")
            print(f"   Purchase Value: ${float(row.get('purchase_value', 0)):.2f}")
            print(f"   Leads: {int(row.get('leads', 0))}")
            print(f"   Status: {row.get('effective_status', 'N/A')}")
            print(f"   Actions raw: {json.dumps(row.get('actions', 'NO ACTIONS FIELD'), ensure_ascii=False)}")
            print("-" * 40)

        total_purchases = sum(int(row.get('purchases', 0)) for row in insights)
        total_spend = sum(float(row.get('spend', 0)) for row in insights)

        print(f"\n💰 Totales del período:")
        print(f"   Gasto total: ${total_spend:.2f}")
        print(f"   Compras totales: {total_purchases}")
        print(f"   ROAS: {(total_purchases * 50 / total_spend) if total_spend > 0 else 0:.2f} (asumiendo valor producto $50)")

        if total_purchases == 0:
            print("\n⚠️ No se detectaron conversiones (purchases = 0)")
            print("   Posibles causas:")
            print("   1. El pixel de Facebook no está configurado correctamente")
            print("   2. El evento de conversión tiene otro nombre (ej: 'Lead', 'CompleteRegistration')")
            print("   3. No hay conversiones en el período seleccionado")
            print("   4. La cuenta no tiene permisos para leer 'actions'")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
