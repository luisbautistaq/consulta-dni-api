from flask import Flask, request, jsonify
from consulta_dni_full_stable import consulta_completa

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "API Consulta DNI Activa 🚀", "status": "ok"})

@app.route('/consulta', methods=['GET'])
def consulta():
    dni = request.args.get('dni', '').strip()
    if not dni:
        return jsonify({"status": "error", "message": "Debe ingresar un DNI"}), 400

    try:
        data = consulta_completa(dni)
        if not data:
            return jsonify({"status": "error", "message": "No se pudo obtener información"}), 500
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
