from flask import Flask, request, jsonify
from consulta_dni_full_stable import consulta_completa
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "OK", "message": "API de Consulta DNI funcionando ✅"})

@app.route('/consulta', methods=['GET'])
def consulta():
    dni = request.args.get('dni')
    if not dni or len(dni) != 8 or not dni.isdigit():
        return jsonify({"error": "DNI inválido. Debe tener 8 dígitos."}), 400
    try:
        data = consulta_completa(dni)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # puerto dinámico para Railway
    app.run(host="0.0.0.0", port=port)
