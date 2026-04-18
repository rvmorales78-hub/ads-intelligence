# webhook_server.py
import os
import stripe
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Importar funciones de la base de datos
from database import update_user_plan, update_user_stripe_info

# Configurar Flask
app = Flask(__name__)

# Configurar claves de Stripe
stripe.api_key = os.getenv('STRIPE_API_KEY')
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
pro_price_id = os.getenv('STRIPE_PRO_PRICE_ID')
enterprise_price_id = os.getenv('STRIPE_ENTERPRISE_PRICE_ID')

# Verificación de variables de entorno al iniciar
missing_vars = []
if not stripe.api_key: missing_vars.append('STRIPE_API_KEY')
if not webhook_secret: missing_vars.append('STRIPE_WEBHOOK_SECRET')
if not pro_price_id: missing_vars.append('STRIPE_PRO_PRICE_ID')
if not enterprise_price_id: missing_vars.append('STRIPE_ENTERPRISE_PRICE_ID')

if missing_vars:
    # Usar print porque el logger puede no estar configurado. En producción, esto debería detener el servidor.
    print(f"FATAL: Faltan variables de entorno de Stripe obligatorias: {', '.join(missing_vars)}")

# Mapeo de Price ID de Stripe a planes internos
PRICE_ID_TO_PLAN = {
    pro_price_id: 'pro',
    enterprise_price_id: 'enterprise',
}
# Eliminar claves nulas si falta algún ID de precio, para evitar errores.
PRICE_ID_TO_PLAN = {k: v for k, v in PRICE_ID_TO_PLAN.items() if k is not None}


@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    # Verificar la firma del webhook
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify(error=str(e)), 400

    # Manejar el evento 'checkout.session.completed'
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')
        
        if not client_reference_id:
            return jsonify(error="client_reference_id no encontrado"), 400
            
        user_id = int(client_reference_id)

        try:
            line_items = stripe.checkout.Session.list_line_items(session.id, limit=1)
            price_id = line_items.data[0].price.id
            new_plan = PRICE_ID_TO_PLAN.get(price_id)

            if new_plan:
                update_user_plan(user_id, new_plan)
                update_user_stripe_info(user_id, stripe_customer_id, stripe_subscription_id)
        except Exception as e:
            return jsonify(error=str(e)), 500

    return jsonify(status='success'), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 4242)) # Usar la variable PORT de Render por defecto
    app.run(host='0.0.0.0', port=port)