"""
RAG-Based Customer Support Assistant
A production-ready Retrieval-Augmented Generation system with LangGraph and HITL
"""

__version__ = "1.0.0"
__author__ = "RAG System Team"

from src.rag_system import RAGSystem
from src.document_processor import DocumentProcessor, DocumentChunk
from src.vector_store import VectorStore, EmbeddingManager
from src.llm_interface import LLMInterface
from src.hitl_manager import HITLManager, EscalationTicket
from src.workflow import RAGWorkflow, GraphState

__all__ = [
    "RAGSystem",
    "DocumentProcessor",
    "DocumentChunk",
    "VectorStore",
    "EmbeddingManager",
    "LLMInterface",
    "HITLManager",
    "EscalationTicket",
    "RAGWorkflow",
    "GraphState",
]
