"""Document processing functionality."""
import logging
from pathlib import Path
from typing import List
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles PDF document loading and processing."""
    
    def __init__(self, chunk_size: int = 7500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        # Archivos PDF fijos (cambia las rutas según tu sistema)
        self.pdf_files = [
            Path("data\pdfs\Capacitación_Norma_de_Educación_Financiera-10dic2024-21.pdf"),
            Path("data\pdfs\ed_financiera_cfn.pdf"),
            Path("data\pdfs\finanzas_dummies_book.pdf")
        ]
    
    def load_pdf(self) -> List:
         documents = []
         for file_path in self.pdf_files:
             try:
                logger.info(f"Loading PDF from {file_path}")
                loader = UnstructuredPDFLoader(str(file_path))
                documents.extend(loader.load())
             except Exception as e:
                logger.error(f"Error loading PDF {file_path}: {e}")
         return documents
    
    def split_documents(self, documents: List) -> List:
        """Split documents into chunks."""
        try:
            logger.info("Splitting documents into chunks")
            return self.splitter.split_documents(documents)
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise 