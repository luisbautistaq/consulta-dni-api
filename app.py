# app.py
from flask import Flask, request, jsonify
from consulta_dni_full_stable import consulta_completa

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "✅ API de consulta DNI activa",
        "uso": "Usa /consulta?dni=12345678 para consultar datos"
    })

@app.route("/consulta", methods=["GET"])
def consulta():
    dni = request.args.get("dni")

    if not dni:
        return jsonify({"error": "Debe enviar el parámetro 'dni'"}), 400
    if not dni.isdigit() or len(dni) != 8:
        return jsonify({"error": "El DNI debe tener 8 dígitos"}), 400

    try:
        data = consulta_completa(dni)
        return jsonify({
            "status": "success",
            "data": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
