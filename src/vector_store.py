from typing import List, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from src.document_processor import DocumentChunk

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

class VectorStore:
    def __init__(self, persist_dir: str, collection_name: str = "customer_support"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_manager = EmbeddingManager()
    
    def add_documents(self, chunks: List[DocumentChunk]):
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_manager.embed_batch(texts)
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=[chunk.metadata for chunk in chunks],
            ids=[f"chunk_{chunk.chunk_id}" for chunk in chunks]
        )
    
    def search(self, query: str, top_k: int = 3) -> Tuple[List[str], List[float]]:
        query_embedding = self.embedding_manager.embed_text(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        documents = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        return documents, distances
    
    def clear(self):
        self.client.delete_collection(self.collection.name)
