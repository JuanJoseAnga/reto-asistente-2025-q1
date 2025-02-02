import logging
from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate

logger = logging.getLogger(__name__)

class LLMManager:
    """Administra la configuración del modelo de lenguaje y los prompts."""
    
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.llm = ChatOllama(model=model_name)
        
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
        """Obtiene un prompt para generación aumentada con recuperación (RAG)."""
        template = """Responde la pregunta basándote ÚNICAMENTE en el siguiente contexto:
        {context}
        Pregunta: {question}
        """
        return ChatPromptTemplate.from_template(template)