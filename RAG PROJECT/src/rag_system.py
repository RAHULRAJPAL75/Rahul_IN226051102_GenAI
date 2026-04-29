from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.llm_interface import LLMInterface
from src.hitl_manager import HITLManager
from src.workflow import RAGWorkflow
from src.config import Config

class RAGSystem:
    def __init__(self):
        self.doc_processor = DocumentProcessor(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
        self.vector_store = VectorStore(Config.CHROMA_PERSIST_DIR)
        self.llm = LLMInterface()
        self.hitl = HITLManager()
        self.workflow = RAGWorkflow(self.vector_store, self.llm, self.hitl)
    
    def ingest_pdf(self, pdf_path: str):
        print(f"Processing PDF: {pdf_path}")
        chunks = self.doc_processor.process_pdf(pdf_path)
        print(f"Created {len(chunks)} chunks")
        
        self.vector_store.add_documents(chunks)
        print("Documents indexed successfully")
    
    def query(self, user_query: str) -> dict:
        result = self.workflow.run(user_query)
        return {
            "query": result["query"],
            "response": result["response"],
            "escalated": result["escalated"],
            "ticket_id": result.get("ticket_id", ""),
            "intent": result["intent_data"].get("intent", "unknown")
        }
    
    def get_pending_tickets(self):
        return self.hitl.get_pending_tickets()
    
    def resolve_ticket(self, ticket_id: str, human_response: str):
        self.hitl.resolve_ticket(ticket_id, human_response)
