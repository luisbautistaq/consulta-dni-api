# app.py
from flask import Flask, request, jsonify
from consulta_dni_full_stable import consulta_completa
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return jsonify({"message": "API Consulta DNI con Playwright", "status": "ok"})

@app.route("/consulta", methods=["GET"])
def consulta():
    dni = request.args.get("dni", "").strip()
    if not dni or len(dni) != 8 or not dni.isdigit():
        return jsonify({"status": "error", "message": "DNI inválido (8 dígitos)"}), 400
    try:
        data = consulta_completa(dni)
        # si todo es None -> error
        if not any([data.get("nombres"), data.get("fecha_nacimiento")]):
            return jsonify({"status": "error", "message": "No se pudo obtener información"}), 500
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
