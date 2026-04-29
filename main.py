import sys
from src.rag_system import RAGSystem

def main():
    print("=" * 60)
    print("RAG-Based Customer Support Assistant")
    print("=" * 60)
    
    rag = RAGSystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        if len(sys.argv) < 3:
            print("Usage: python main.py ingest <pdf_path>")
            return
        
        pdf_path = sys.argv[2]
        rag.ingest_pdf(pdf_path)
        print("\nPDF ingestion complete!")
        return
    
    print("\nCommands:")
    print("  - Type your question")
    print("  - 'tickets' to view pending escalations")
    print("  - 'resolve <ticket_id> <response>' to resolve a ticket")
    print("  - 'exit' to quit")
    print()
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        if user_input.lower() == "tickets":
            tickets = rag.get_pending_tickets()
            if not tickets:
                print("No pending tickets.")
            else:
                for ticket in tickets:
                    print(f"\n[{ticket.ticket_id}]")
                    print(f"Query: {ticket.query}")
                    print(f"Reason: {ticket.reason}")
                    print(f"Time: {ticket.timestamp}")
            continue
        
        if user_input.lower().startswith("resolve "):
            parts = user_input.split(maxsplit=2)
            if len(parts) < 3:
                print("Usage: resolve <ticket_id> <response>")
                continue
            ticket_id = parts[1]
            response = parts[2]
            rag.resolve_ticket(ticket_id, response)
            print(f"Ticket {ticket_id} resolved.")
            continue
        
        result = rag.query(user_input)
        
        print(f"\nAssistant: {result['response']}")
        if result['escalated']:
            print(f"\n[ESCALATED] Ticket: {result['ticket_id']}")

if __name__ == "__main__":
    main()
