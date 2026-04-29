from typing import List
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    content: str
    metadata: dict
    chunk_id: int

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_pdf(self, pdf_path: str) -> str:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def chunk_text(self, text: str, source: str = "document") -> List[DocumentChunk]:
        chunks = self.text_splitter.split_text(text)
        return [
            DocumentChunk(
                content=chunk,
                metadata={"source": source, "chunk_index": i},
                chunk_id=i
            )
            for i, chunk in enumerate(chunks)
        ]
    
    def process_pdf(self, pdf_path: str) -> List[DocumentChunk]:
        text = self.load_pdf(pdf_path)
        return self.chunk_text(text, source=pdf_path)
