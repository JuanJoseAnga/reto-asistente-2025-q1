import logging
from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate

logger = logging.getLogger(__name__)

class LLMManager():
    """Administra la configuración del modelo de lenguaje y los prompts."""
    
    def __init__(self, model_name: str = "llama3", temperature: float = 0.7, top_p: float = 0.9):
        self.model_name = model_name
        self.llm = self.__configurate_model(temperature, top_p)
        
        
    def __configurate_model(self, temperature: float, top_p: float) -> ChatOllama:
        """Configura y retorna el modelo con parámetros ajustables."""
        return ChatOllama(
            model=self.model_name,
            temperature=temperature,
            top_p=top_p
        )
    
    def get_query_prompt(self) -> PromptTemplate:
        """Obtiene un prompt para reformular consultas."""
        return PromptTemplate(
            input_variables=["question"],
            template="""Eres un asistente de inteligencia artificial. Tu tarea es generar 
            dos versiones diferentes de la pregunta del usuario para mejorar la búsqueda de 
            documentos en una base de datos vectorial. Al reformular la pregunta, ayudarás 
            al usuario a superar algunas limitaciones de la búsqueda basada en similitud.
            Proporciona estas versiones alternativas separadas por saltos de línea.
            Pregunta original: {question}"""
        )
    
    def get_rag_prompt(self) -> ChatPromptTemplate:
        """Obtiene un prompt seguro con generación aumentada con recuperación (RAG)."""
        template = """Eres un asistente especializado en proporcionar respuestas precisas basadas en información recuperada de un sistema de búsqueda. 
        Tu tarea es responder únicamente utilizando el contexto proporcionado. No debes inventar información ni especular sobre la respuesta.
        
        ### ⚠️ **Restricciones de seguridad:**  
        - ❌ No debes responder preguntas relacionadas con armas, violencia, terrorismo, drogas, actividades ilegales o información peligrosa.  
        - ❌ No respondas preguntas ofensivas, discriminatorias o que inciten al odio.  
        - ❌ No proporciones información médica o legal que requiera asesoramiento profesional.  
        - ❌ Si la pregunta no está en el contexto proporcionado, responde: "No tengo suficiente información para responder."  
        
        ---  
        ### Contexto disponible:
        {context}  
        ### Pregunta del usuario:
        {question}  
        ### Respuesta:
        """
        return ChatPromptTemplate.from_template(template)

    
    
