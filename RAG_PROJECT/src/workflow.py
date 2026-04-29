from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from src.vector_store import VectorStore
from src.llm_interface import LLMInterface
from src.hitl_manager import HITLManager
from src.config import Config

class GraphState(TypedDict):
    query: str
    intent_data: dict
    retrieved_docs: List[str]
    retrieval_scores: List[float]
    response: str
    escalated: bool
    escalation_reason: str
    ticket_id: str

class RAGWorkflow:
    def __init__(self, vector_store: VectorStore, llm: LLMInterface, hitl: HITLManager):
        self.vector_store = vector_store
        self.llm = llm
        self.hitl = hitl
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(GraphState)
        
        workflow.add_node("classify_intent", self.classify_intent_node)
        workflow.add_node("retrieve_context", self.retrieve_context_node)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("escalate_to_human", self.escalate_node)
        
        workflow.set_entry_point("classify_intent")
        
        workflow.add_edge("classify_intent", "retrieve_context")
        workflow.add_conditional_edges(
            "retrieve_context",
            self.should_escalate,
            {
                "escalate": "escalate_to_human",
                "continue": "generate_response"
            }
        )
        workflow.add_edge("generate_response", END)
        workflow.add_edge("escalate_to_human", END)
        
        return workflow.compile()
    
    def classify_intent_node(self, state: GraphState) -> GraphState:
        intent_data = self.llm.classify_intent(state["query"])
        state["intent_data"] = intent_data
        return state
    
    def retrieve_context_node(self, state: GraphState) -> GraphState:
        docs, scores = self.vector_store.search(state["query"], top_k=3)
        state["retrieved_docs"] = docs
        state["retrieval_scores"] = scores
        return state
    
    def should_escalate(self, state: GraphState) -> str:
        avg_score = sum(state["retrieval_scores"]) / len(state["retrieval_scores"]) if state["retrieval_scores"] else 0
        confidence = 1 - avg_score
        
        should_esc, reason = self.hitl.should_escalate(
            state["query"],
            state["intent_data"],
            confidence,
            Config.CONFIDENCE_THRESHOLD
        )
        
        if should_esc:
            state["escalation_reason"] = reason
            return "escalate"
        return "continue"
    
    def generate_response_node(self, state: GraphState) -> GraphState:
        response = self.llm.generate_response(state["query"], state["retrieved_docs"])
        state["response"] = response
        state["escalated"] = False
        return state
    
    def escalate_node(self, state: GraphState) -> GraphState:
        ticket = self.hitl.create_ticket(
            state["query"],
            state["retrieved_docs"],
            state["escalation_reason"]
        )
        state["escalated"] = True
        state["ticket_id"] = ticket.ticket_id
        state["response"] = f"Your query has been escalated to a human agent. Ticket ID: {ticket.ticket_id}\nReason: {state['escalation_reason']}"
        return state
    
    def run(self, query: str) -> dict:
        initial_state = {
            "query": query,
            "intent_data": {},
            "retrieved_docs": [],
            "retrieval_scores": [],
            "response": "",
            "escalated": False,
            "escalation_reason": "",
            "ticket_id": ""
        }
        
        result = self.graph.invoke(initial_state)
        return result
