from flask import Flask, request
from flask_restful import Api, Resource
import logging

from service.rag import RAGPipeline
from model.modellm import LLMManager

logger = logging.getLogger(__name__)

# Inicializar los módulos del sistema RAG
llm_manager = LLMManager()
rag_pipeline = RAGPipeline( llm_manager)

class RAGHandler(Resource):
    def post(self):
        global rag_pipeline
        try:
            # Asegurar que rag_pipeline está inicializado
            if rag_pipeline is None:
                return {"error": "Pipeline RAG no inicializado."}, 500

            # Validar entrada
            data = request.get_json()
            if not data or "question" not in data:
                return {"error": "Debe enviar una pregunta en el formato {'question': 'texto'}"}, 400

            question = data["question"]
            logger.info(f"Procesando pregunta: {question}")

            # Obtener respuesta
            response = rag_pipeline.get_response(question)

            # Log para inspeccionar el tipo de respuesta
            logger.info(f"Tipo de respuesta: {type(response)}")

            # Asegurar que la respuesta sea serializable
            if isinstance(response, (dict, list, str)):
                return {"respuesta": response}, 200
            else:
                return {"respuesta": str(response)}, 200

        except Exception as e:
            logger.error(f"Error en la API: {e}", exc_info=True)
            return {"error": str(e)}, 500 
        
