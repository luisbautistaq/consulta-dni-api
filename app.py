from flask import Flask, request, jsonify
import nest_asyncio, asyncio
from consulta_dni_playwright import consulta_dni

nest_asyncio.apply()
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ API de consulta de DNI en Render (Playwright)."

@app.route('/consulta')
def consulta():
    dni = request.args.get("dni", "").strip()
    if not dni.isdigit() or len(dni) != 8:
        return jsonify({"status": "error", "message": "DNI inválido"}), 400

    result = asyncio.get_event_loop().run_until_complete(consulta_dni(dni))
    return jsonify({"status": "success", "data": result})
