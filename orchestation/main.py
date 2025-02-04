from flask import Flask, request, jsonify
from flask_restful import Api
from dotenv import load_dotenv
from controller.orchestrationController import OrchestrationController

# Cargar variables de entorno antes de importar módulos que las usan
load_dotenv()

app = Flask(__name__)
api = Api(app)

PORT = 8000

# Instancia del controlador de orquestación
orchestration_controller = OrchestrationController()

@app.route('/orchestrate', methods=['POST'])
def orchestrate():
    """Endpoint de orquestación que recibe consultas y las procesa."""
    data = request.get_json()

    if not data or "consulta" not in data:
        return jsonify({"error": True, "message": "La consulta no fue proporcionada."}), 400

    user_query = data.get('consulta')
    pdf_data = data.get('pdfbase64')

    # Procesamos la consulta a través del controlador de orquestación
    result = orchestration_controller.handle_query(user_query, pdf_data)

    return jsonify(result)

if __name__ == "__main__":
    print(f"🚀 Flask API iniciando en http://127.0.0.1:{PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=True)
