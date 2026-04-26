import os, re, requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)

# CONFIGURACIÓN (Asegúrate de que coincidan con tu Firefly)
FIREFLY_BASE_URL = "http://localhost:8080/api/v1/transactions"
FIREFLY_TOKEN = os.getenv("INSOMNIA_TEST_TOKEN")
MP_ACCOUNT_ID = 1  # ID de tu cuenta de Mercado Pago
EXPENSE_ID = 2     # ID de tu cuenta de Gastos Varios
REVENUE_ID = 3     # ID de tu cuenta de Ingresos Varios

headers = {
    "Authorization": f"Bearer {FIREFLY_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def enviar_a_firefly(descripcion, monto, tipo):
    # Lógica de flujo:
    # Si es depósito: Viene de Ingresos (REVENUE) -> Va a Mercado Pago (MP)
    # Si es retiro: Viene de Mercado Pago (MP) -> Va a Gastos (EXPENSE)
    source_id = REVENUE_ID if tipo == "deposit" else MP_ACCOUNT_ID
    dest_id = MP_ACCOUNT_ID if tipo == "deposit" else EXPENSE_ID

    payload = {
        "error_if_duplicate_hash": True,
        "transactions": [{
            "type": "deposit" if tipo == "deposit" else "withdrawal",
            "description": descripcion,
            "amount": str(monto),
            "date": datetime.now().isoformat(),
            "source_id": source_id,
            "destination_id": dest_id,
            "notes": "Automatizado vía Interceptor Android"
        }]
    }
    
    res = requests.post(FIREFLY_BASE_URL, headers=headers, json=payload)
    return res.status_code

@app.route('/notificacion', methods=['POST'])
def procesar_notificacion():
    data = request.get_json(force=True, silent=True)
    if not data: return jsonify({"error": "No JSON"}), 400

    # Combinamos título y texto para no perdernos nada
    titulo = data.get("titulo", "")
    cuerpo = data.get("texto", "")
    contenido_completo = f"{titulo} {cuerpo}"
    
    print(f"\n--- PROCESANDO NOTIFICACIÓN ---")
    print(f"Contenido completo: {contenido_completo}")

    # El mismo Regex potente de antes
    match = re.search(r'\$\s?([\d\.]+,\d{2}|[\d\.]+)', contenido_completo)
    
    if match:
        monto_str = match.group(1).replace('.', '').replace(',', '.')
        monto = float(monto_str)
        print(f" Monto detectado: {monto}")
        
        # Analizamos el contenido completo para decidir si es ingreso o gasto
        palabras_ingreso = ["recibiste", "ingresó", "acreditamos", "ingresaste", "recibido"]
        tipo = "deposit" if any(x in contenido_completo.lower() for x in palabras_ingreso) else "withdrawal"
        
        # Enviar a Firefly usando el contenido completo como descripción
        status = enviar_a_firefly(contenido_completo, monto, tipo)
        print(f" Respuesta API Firefly: {status}")
        
        if status in [200, 201]:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "api_error", "code": status}), 500
    
    print(" No se encontró ningún monto en título ni en cuerpo.")
    return jsonify({"status": "no_amount_found"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)