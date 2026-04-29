from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class EscalationTicket:
    ticket_id: str
    query: str
    context: list
    reason: str
    timestamp: datetime
    status: str = "pending"
    human_response: Optional[str] = None

class HITLManager:
    def __init__(self):
        self.pending_tickets = {}
        self.resolved_tickets = {}
    
    def should_escalate(self, query: str, intent_data: dict, retrieval_confidence: float, threshold: float = 0.7) -> tuple[bool, str]:
        if intent_data.get("requires_human", False):
            return True, "Intent classified as requiring human intervention"
        
        if retrieval_confidence < threshold:
            return True, f"Low retrieval confidence: {retrieval_confidence:.2f}"
        
        if intent_data.get("intent") in ["complaint", "technical_issue"]:
            return True, f"Sensitive intent: {intent_data.get('intent')}"
        
        if intent_data.get("confidence", 1.0) < 0.6:
            return True, f"Low intent confidence: {intent_data.get('confidence'):.2f}"
        
        return False, ""
    
    def create_ticket(self, query: str, context: list, reason: str) -> EscalationTicket:
        ticket_id = f"TICKET_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        ticket = EscalationTicket(
            ticket_id=ticket_id,
            query=query,
            context=context,
            reason=reason,
            timestamp=datetime.now()
        )
        self.pending_tickets[ticket_id] = ticket
        return ticket
    
    def resolve_ticket(self, ticket_id: str, human_response: str):
        if ticket_id in self.pending_tickets:
            ticket = self.pending_tickets[ticket_id]
            ticket.status = "resolved"
            ticket.human_response = human_response
            self.resolved_tickets[ticket_id] = ticket
            del self.pending_tickets[ticket_id]
    
    def get_pending_tickets(self):
        return list(self.pending_tickets.values())
    
    def save_tickets(self, filepath: str):
        data = {
            "pending": [vars(t) for t in self.pending_tickets.values()],
            "resolved": [vars(t) for t in self.resolved_tickets.values()]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
