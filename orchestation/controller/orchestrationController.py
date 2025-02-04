import logging
import os
import requests
from model.modellm import LLMManager

logging.basicConfig(level=logging.DEBUG)

ASSISTANT_HOST = os.getenv("ASSISTANT_HOST", "http://localhost:8000")

class OrchestrationController():
    """Controlador de orquestación encargado de procesar la consulta del usuario y enviarla al servicio adecuado."""

    def __init__(self):
        self.llm_manager = LLMManager()  

    def classify_query(self, query):
        """Clasifica la consulta del usuario en función de su intención y seguridad."""

        prompt = """Eres un moderador estricto encargado de validar si una pregunta es tóxica y clasificar su intención.  
        
                ### 🚨 **Normas de Moderación:**  
                - Si la pregunta menciona **violencia, armas, drogas, actividades ilegales o contenido NSFW**, responde con `"toxico"`.  
                - Si la pregunta es ambigua o no encaja en ninguna categoría, responde `"toxico"`.

                ### 📌 **Categorías de Intención:**  
                1️⃣ **"chat_rag"** → Preguntas sobre **educación financiera, inversiones, análisis económico y finanzas**.  
                2️⃣ **"analisis_pdf"** → Consultas sobre **análisis de documentos financieros o estados de cuenta en PDF**.  
                3️⃣ **"asesor_compras"** → Consultas sobre **recomendaciones de productos y asesoramiento de compras**.  

                🔍 **Consulta del usuario:**  
                "{question}"  

                🔽 **Responde solo con una de las siguientes opciones:** `"toxico", "chat_rag", "analisis_pdf", "asesor_compras"`
                """

        # Formateamos el prompt con la consulta del usuario
        formatted_prompt = self.llm_manager.get_classification_prompt().format(question=query)

        # Generamos la respuesta con el modelo LLM
        response = self.llm_manager.llm.invoke(formatted_prompt)

        # Extraemos el contenido
        intent = response.content.strip().lower()

        # Validamos la respuesta
        valid_intents = ["toxico", "chat_rag", "analisis_pdf", "asesor_compras"]
        if intent not in valid_intents:
            logging.error(f"❌ Intención no válida recibida: {intent}")
            return "toxico"  # Evita valores incorrectos

        logging.info(f"✅ Intención clasificada: {intent}")
        return intent


    def send_to_endpoint(self, endpoint, query, pdf_data):
        """Envía la consulta al endpoint adecuado con la información necesaria."""
        url = f"{ASSISTANT_HOST}{endpoint}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "query": query,
            "pdf_encode": pdf_data
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"⚠️ Error en la comunicación con el servidor (Status {response.status_code})")
                return {"error": True, "message": "Error en la comunicación con el servidor.", "status_code": response.status_code}
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Error al hacer la solicitud: {e}")
            return {"error": True, "message": str(e)}

    def handle_query(self, query, pdf_data=None):
        """Orquesta el procesamiento de la consulta, verificando toxicidad, clasificando intención y generando respuestas."""

        # 1️⃣ Validamos si la consulta es tóxica
        intent = self.classify_query(query)

        if intent == "toxico":
            return {"assistant_response": "Lo siento, no puedo ayudarte con esta consulta."}

        # 2️⃣ Determinamos el endpoint según la intención clasificada
        endpoints = {
            "chat_rag": "/assistant/rag",
            "analisis_pdf": "/assistant/analyze-pdf",
            "asesor_compras": "/assistant/shopping-advisor"
        }

        endpoint = endpoints.get(intent)
        if not endpoint:
            return {"assistant_response": "Lo siento, no reconozco la intención de tu consulta."}

        logging.info(f"📡 Enrutando a: {endpoint}")
        return self.send_to_endpoint(endpoint, query, pdf_data)
