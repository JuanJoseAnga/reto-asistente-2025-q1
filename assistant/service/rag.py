"""RAG pipeline implementation."""
import logging
from typing import Any, Dict
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever
from model.modellm import LLMManager
import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

logger = logging.getLogger(__name__)

class RAGPipeline:
  
    def __init__(self, llm_manager: LLMManager):
        self.retriveal = self._getRetriveal()
        self.llm_manager = llm_manager
        self.retriever = self._setup_retriever()
        self.chain = self._setup_chain()

    def _getRetriveal(self):
        persistent_client = chromadb.HttpClient()
        vector_store_from_client = Chroma(
            client=persistent_client,
            collection_name="base_vectorial",
            embedding_function=OllamaEmbeddings(model="nomic-embed-text")
        )
        return vector_store_from_client.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    
    def _setup_retriever(self) -> MultiQueryRetriever:
        """Configura el recuperador de información multi-consulta."""
        try:
            return MultiQueryRetriever.from_llm(
                retriever=self.retriveal,
                llm=self.llm_manager.llm,
                prompt=self.llm_manager.get_query_prompt()
            )
        except Exception as e:
            logger.error(f"Error setting up retriever: {e}")
            raise
    
    def _setup_chain(self) -> Any:
        """Configura la cadena RAG."""
        try:
            return (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.llm_manager.get_rag_prompt()
                | self.llm_manager.llm
                | StrOutputParser()
            )
        except Exception as e:
            logger.error(f"Error setting up chain: {e}")
            raise
    
    def get_response(self, question: str) -> str:
        """Obtiene una respuesta a partir de la pregunta usando la pipeline RAG."""
        try:
            logger.info(f"Obtener respuesta a una pregunta: {question}")
            return self.chain.invoke(question)
        except Exception as e:
            logger.error(f"Error obteenr respuesta: {e}")
            raise 