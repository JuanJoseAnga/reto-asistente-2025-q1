from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv

load_dotenv()

from utils.consulta import Consulta
from utils.asistente_docs import RAGHandler

app = Flask(__name__)
api = Api(app)

PORT = 5000

api.add_resource(RAGHandler, "/assistant/rag")
api.add_resource(Consulta, "/assistant/analyze-pdf")
#api.add_resource(ShoppingAdvisorAdapter, "/assistant/shopping-advisor")

if __name__ == "__main__":
    print(f"🚀 Flask API iniciando en http://127.0.0.1:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)