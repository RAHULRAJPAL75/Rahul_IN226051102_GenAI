from typing import List
from openai import OpenAI
from src.config import Config

class LLMInterface:
    def __init__(self, api_key: str = None, model: str = None):
        self.client = OpenAI(api_key=api_key or Config.OPENAI_API_KEY)
        self.model = model or Config.LLM_MODEL
    
    def generate_response(self, query: str, context: List[str]) -> str:
        context_text = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(context)])
        
        prompt = f"""You are a customer support assistant. Answer the user's question based on the provided context.

Context:
{context_text}

User Question: {query}

Instructions:
- Answer based only on the provided context
- Be concise and helpful
- If the context doesn't contain the answer, say "I don't have enough information to answer this question."

Answer:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def classify_intent(self, query: str) -> dict:
        prompt = f"""Classify the following customer query:

Query: {query}

Respond with JSON containing:
- "intent": one of ["simple_question", "complex_question", "complaint", "technical_issue"]
- "confidence": float between 0 and 1
- "requires_human": boolean

JSON:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"intent": "simple_question", "confidence": 0.5, "requires_human": False}
