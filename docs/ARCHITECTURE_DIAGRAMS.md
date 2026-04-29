# SYSTEM ARCHITECTURE DIAGRAMS

## 1. COMPLETE SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                          │
│                                                                         │
│  ┌──────────────────┐              ┌──────────────────┐               │
│  │   CLI Interface  │              │  API (Future)    │               │
│  │    (main.py)     │              │   FastAPI/REST   │               │
│  └────────┬─────────┘              └────────┬─────────┘               │
└───────────┼──────────────────────────────────┼─────────────────────────┘
            │                                  │
            └──────────────┬───────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────────────┐
│                          ▼                                               │
│                   RAG SYSTEM CORE                                        │
│                  (rag_system.py)                                         │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │              LANGGRAPH WORKFLOW ENGINE                         │    │
│  │                  (workflow.py)                                 │    │
│  │                                                                │    │
│  │   ┌──────────────┐      ┌──────────────┐      ┌────────────┐ │    │
│  │   │  Node 1:     │      │  Node 2:     │      │  Node 3:   │ │    │
│  │   │  Classify    │─────▶│  Retrieve    │─────▶│  Generate  │ │    │
│  │   │  Intent      │      │  Context     │      │  Response  │ │    │
│  │   └──────────────┘      └──────┬───────┘      └────────────┘ │    │
│  │                                 │                             │    │
│  │                                 │ [Conditional Routing]       │    │
│  │                                 ▼                             │    │
│  │                         ┌──────────────┐                      │    │
│  │                         │  Node 4:     │                      │    │
│  │                         │  Escalate    │                      │    │
│  │                         │  to Human    │                      │    │
│  │                         └──────────────┘                      │    │
│  │                                                                │    │
│  │  State: {query, intent_data, retrieved_docs, response, ...}   │    │
│  └────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  LLM INTERFACE   │  │  VECTOR STORE    │  │  HITL MANAGER    │
│ (llm_interface)  │  │ (vector_store)   │  │ (hitl_manager)   │
│                  │  │                  │  │                  │
│ ┌──────────────┐ │  │ ┌──────────────┐ │  │ ┌──────────────┐ │
│ │ OpenAI API   │ │  │ │  ChromaDB    │ │  │ │ Escalation   │ │
│ │ GPT-3.5      │ │  │ │  Persistent  │ │  │ │ Tickets      │ │
│ │              │ │  │ │  HNSW Index  │ │  │ │              │ │
│ │ - Classify   │ │  │ │              │ │  │ │ - Create     │ │
│ │ - Generate   │ │  │ │ - Store      │ │  │ │ - Manage     │ │
│ └──────────────┘ │  │ │ - Search     │ │  │ │ - Resolve    │ │
└──────────────────┘  │ └──────────────┘ │  │ └──────────────┘ │
                      │        ▲         │  └──────────────────┘
                      │        │         │
                      │ ┌──────┴───────┐ │
                      │ │  Embedding   │ │
                      │ │  Manager     │ │
                      │ │              │ │
                      │ │ Sentence     │ │
                      │ │ Transformers │ │
                      │ │ (384-dim)    │ │
                      │ └──────────────┘ │
                      └──────────────────┘
                               ▲
                               │
                      ┌────────┴─────────┐
                      │  DOCUMENT        │
                      │  PROCESSOR       │
                      │ (document_       │
                      │  processor)      │
                      │                  │
                      │ ┌──────────────┐ │
                      │ │ PDF Loader   │ │
                      │ │ (PyPDF)      │ │
                      │ └──────┬───────┘ │
                      │        │         │
                      │ ┌──────▼───────┐ │
                      │ │ Text Chunker │ │
                      │ │ (500 chars)  │ │
                      │ │ (50 overlap) │ │
                      │ └──────────────┘ │
                      └──────────────────┘
                               ▲
                               │
                      ┌────────┴─────────┐
                      │  KNOWLEDGE BASE  │
                      │                  │
                      │  PDF Documents   │
                      │  Text Files      │
                      └──────────────────┘
```

---

## 2. DATA FLOW - INGESTION PIPELINE

```
┌─────────────────┐
│  PDF Document   │
│  (Knowledge     │
│   Base)         │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  STEP 1: Load PDF                   │
│  ┌───────────────────────────────┐  │
│  │ PyPDF Reader                  │  │
│  │ - Extract text from pages     │  │
│  │ - Concatenate all pages       │  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │ Raw Text
         ▼
┌─────────────────────────────────────┐
│  STEP 2: Chunk Text                 │
│  ┌───────────────────────────────┐  │
│  │ RecursiveCharacterTextSplitter│  │
│  │ - Chunk size: 500 chars       │  │
│  │ - Overlap: 50 chars           │  │
│  │ - Separators: \n\n, \n, ., ' '│  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │ List[DocumentChunk]
         ▼
┌─────────────────────────────────────┐
│  STEP 3: Generate Embeddings        │
│  ┌───────────────────────────────┐  │
│  │ SentenceTransformers          │  │
│  │ Model: all-MiniLM-L6-v2       │  │
│  │ Output: 384-dim vectors       │  │
│  │ Batch processing: 100 chunks  │  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │ List[Embedding]
         ▼
┌─────────────────────────────────────┐
│  STEP 4: Store in Vector DB         │
│  ┌───────────────────────────────┐  │
│  │ ChromaDB                      │  │
│  │ - Store embeddings            │  │
│  │ - Store documents             │  │
│  │ - Store metadata              │  │
│  │ - Build HNSW index            │  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Ready for      │
│  Queries!       │
└─────────────────┘
```

---

## 3. DATA FLOW - QUERY PIPELINE

```
┌─────────────────┐
│  User Query     │
│  "How to reset  │
│   password?"    │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  LANGGRAPH WORKFLOW START                                │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  NODE 1: Classify Intent                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │ LLM Call (GPT-3.5)                                │  │
│  │ Input: User query                                 │  │
│  │ Output: {                                         │  │
│  │   intent: "simple_question",                      │  │
│  │   confidence: 0.95,                               │  │
│  │   requires_human: false                           │  │
│  │ }                                                 │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │ State updated with intent_data
         ▼
┌─────────────────────────────────────────────────────────┐
│  NODE 2: Retrieve Context                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 1. Embed query (SentenceTransformers)            │  │
│  │    → 384-dim vector                               │  │
│  │                                                   │  │
│  │ 2. Search ChromaDB (Cosine similarity)           │  │
│  │    → Top-3 chunks                                 │  │
│  │                                                   │  │
│  │ 3. Return:                                        │  │
│  │    - retrieved_docs: [chunk1, chunk2, chunk3]    │  │
│  │    - retrieval_scores: [0.15, 0.23, 0.31]        │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │ State updated with context
         ▼
┌─────────────────────────────────────────────────────────┐
│  ROUTING DECISION: should_escalate()                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Check:                                            │  │
│  │ ✓ requires_human? → No                            │  │
│  │ ✓ retrieval_confidence < 0.7? → No (0.85)        │  │
│  │ ✓ intent = complaint/technical? → No             │  │
│  │ ✓ intent_confidence < 0.6? → No (0.95)           │  │
│  │                                                   │  │
│  │ Decision: CONTINUE (AI handles)                   │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  NODE 3: Generate Response                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ LLM Call (GPT-3.5)                                │  │
│  │ Input:                                            │  │
│  │   - User query                                    │  │
│  │   - Context chunks (3)                            │  │
│  │                                                   │  │
│  │ Prompt:                                           │  │
│  │   "You are a customer support assistant.         │  │
│  │    Answer based on context..."                    │  │
│  │                                                   │  │
│  │ Output:                                           │  │
│  │   "To reset your password, click the             │  │
│  │    'Forgot Password' link..."                     │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │ State updated with response
         ▼
┌─────────────────────────────────────────────────────────┐
│  WORKFLOW END                                           │
│  Return: {                                              │
│    query: "How to reset password?",                     │
│    response: "To reset your password...",               │
│    escalated: false,                                    │
│    intent: "simple_question"                            │
│  }                                                      │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  User receives  │
│  AI Answer      │
└─────────────────┘
```

---

## 4. ESCALATION FLOW

```
┌─────────────────┐
│  User Query     │
│  "Your service  │
│   is terrible!" │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  NODE 1: Classify Intent            │
│  Output: {                          │
│    intent: "complaint",             │
│    confidence: 0.98,                │
│    requires_human: false            │
│  }                                  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  NODE 2: Retrieve Context           │
│  (Still retrieves for human agent)  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  ROUTING DECISION                   │
│  ✗ intent = "complaint"             │
│  → ESCALATE                         │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  NODE 4: Escalate to Human          │
│  ┌───────────────────────────────┐  │
│  │ 1. Create EscalationTicket    │  │
│  │    - ticket_id: TICKET_...    │  │
│  │    - query: "Your service..." │  │
│  │    - context: [chunks]        │  │
│  │    - reason: "Sensitive..."   │  │
│  │    - status: "pending"        │  │
│  │                               │  │
│  │ 2. Add to pending queue       │  │
│  │                               │  │
│  │ 3. Generate escalation msg    │  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  User receives:                     │
│  "Your query has been escalated     │
│   to a human agent.                 │
│   Ticket ID: TICKET_20240115123045" │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Human Agent:                       │
│  1. Views ticket in queue           │
│  2. Reviews query + context         │
│  3. Crafts empathetic response      │
│  4. Resolves ticket                 │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  User receives human response       │
└─────────────────────────────────────┘
```

---

## 5. COMPONENT INTERACTION DIAGRAM

```
┌──────────────────────────────────────────────────────────────┐
│                      RAGSystem                               │
│  (Main Orchestrator - rag_system.py)                         │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ ingest_pdf │  │   query    │  │get_tickets │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
└────────┼───────────────┼───────────────┼──────────────────┘
         │               │               │
         │               │               │
    ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
    │Document │     │Workflow │    │  HITL   │
    │Processor│     │ Engine  │    │ Manager │
    └────┬────┘     └────┬────┘    └────┬────┘
         │               │               │
         │          ┌────▼────┐          │
         │          │   LLM   │          │
         │          │Interface│          │
         │          └────┬────┘          │
         │               │               │
    ┌────▼───────────────▼───────────────┘
    │      Vector Store                  
    │   (Embeddings + ChromaDB)          
    └────────────────────────────────────┘

Interaction Flow:
1. RAGSystem.ingest_pdf() → DocumentProcessor → VectorStore
2. RAGSystem.query() → Workflow → LLM + VectorStore + HITL
3. RAGSystem.get_tickets() → HITL
```

---

## 6. TECHNOLOGY STACK DIAGRAM

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                    │
│  ┌──────────────┐              ┌──────────────┐        │
│  │     CLI      │              │  API (Future)│        │
│  │   Python     │              │   FastAPI    │        │
│  └──────────────┘              └──────────────┘        │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │              LangGraph                           │  │
│  │  (Workflow Engine, State Management, Routing)    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   LangChain  │  │    OpenAI    │  │   Custom    │  │
│  │  (Document   │  │  (GPT-3.5)   │  │   Logic     │  │
│  │  Processing) │  │              │  │   (HITL)    │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│                      DATA LAYER                         │
│  ┌──────────────┐              ┌──────────────┐        │
│  │   ChromaDB   │              │ Sentence     │        │
│  │  (Vector DB) │              │ Transformers │        │
│  │              │              │ (Embeddings) │        │
│  └──────────────┘              └──────────────┘        │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                        │
│  ┌──────────────┐              ┌──────────────┐        │
│  │  File System │              │   Memory     │        │
│  │  (PDF, DB)   │              │  (Cache)     │        │
│  └──────────────┘              └──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

**End of Architecture Diagrams**
