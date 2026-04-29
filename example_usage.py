"""
Example Usage of RAG Customer Support Assistant
This script demonstrates how to use the RAG system programmatically
"""

from src.rag_system import RAGSystem

def main():
    print("=" * 60)
    print("RAG System - Example Usage")
    print("=" * 60)
 
    print("\n1. Initializing RAG System...")
    rag = RAGSystem()

    print("\n2. Ingesting knowledge base...")
    pdf_path = "data/sample_knowledge_base.txt"
    rag.ingest_pdf(pdf_path)
    
    queries = [
        "What is the price of CloudSync Pro?",
        "How do I reset my password?",
        "I'm very unhappy with your service!",
        "My app keeps crashing with error 500",
        "What browsers are supported?",
    ]
    
    print("\n3. Testing queries...")
    print("-" * 60)
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = rag.query(query)
        
        print(f"Intent: {result['intent']}")
        print(f"Escalated: {result['escalated']}")
        
        if result['escalated']:
            print(f"Ticket ID: {result['ticket_id']}")
        
        print(f"Response: {result['response'][:200]}...")
        print("-" * 60)
    
    # View pending tickets
    print("\n4. Pending Escalations:")
    tickets = rag.get_pending_tickets()
    
    if tickets:
        for ticket in tickets:
            print(f"\n[{ticket.ticket_id}]")
            print(f"Query: {ticket.query}")
            print(f"Reason: {ticket.reason}")
            print(f"Status: {ticket.status}")
    else:
        print("No pending tickets.")
 
    if tickets:
        print("\n5. Resolving first ticket...")
        ticket_id = tickets[0].ticket_id
        human_response = "I apologize for the inconvenience. Let me help you resolve this issue..."
        rag.resolve_ticket(ticket_id, human_response)
        print(f"Ticket {ticket_id} resolved!")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
