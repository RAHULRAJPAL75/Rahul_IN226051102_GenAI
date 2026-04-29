import unittest
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.hitl_manager import HITLManager

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
    
    def test_chunking(self):
        text = "This is a test. " * 50
        chunks = self.processor.chunk_text(text)
        self.assertGreater(len(chunks), 0)
        self.assertTrue(all(len(c.content) <= 120 for c in chunks))

class TestHITLManager(unittest.TestCase):
    def setUp(self):
        self.hitl = HITLManager()
    
    def test_escalation_logic(self):
        intent_data = {"intent": "complaint", "confidence": 0.9, "requires_human": False}
        should_esc, reason = self.hitl.should_escalate("I'm unhappy", intent_data, 0.8)
        self.assertTrue(should_esc)
    
    def test_ticket_creation(self):
        ticket = self.hitl.create_ticket("Test query", [], "Test reason")
        self.assertIn("TICKET_", ticket.ticket_id)
        self.assertEqual(ticket.status, "pending")

class TestVectorStore(unittest.TestCase):
    def setUp(self):
        self.store = VectorStore("./test_chroma", "test_collection")
    
    def tearDown(self):
        self.store.clear()
    
    def test_add_and_search(self):
        from src.document_processor import DocumentChunk
        chunks = [
            DocumentChunk("Python is a programming language", {"source": "test"}, 0),
            DocumentChunk("Java is also a programming language", {"source": "test"}, 1)
        ]
        self.store.add_documents(chunks)
        
        docs, scores = self.store.search("What is Python?", top_k=1)
        self.assertEqual(len(docs), 1)
        self.assertIn("Python", docs[0])

if __name__ == "__main__":
    unittest.main()
