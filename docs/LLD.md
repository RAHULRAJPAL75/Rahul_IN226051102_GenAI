# LOW-LEVEL DESIGN (LLD)
## RAG-Based Customer Support Assistant - Implementation Details

---

## 1. MODULE-LEVEL DESIGN

### 1.1 Document Processing Module

**File:** `src/document_processor.py`

**Class: DocumentProcessor**

```python
Attributes:
- chunk_size: int (default: 500)
- chunk_overlap: int (default: 50)
- text_splitter: RecursiveCharacterTextSplitter

Methods:
- load_pdf(pdf_path: str) -> str
  Input: Path to PDF file
  Output: Extracted text as string
  Logic: Iterate through pages, extract text, concatenate
  
- chunk_text(text: str, source: str) -> List[DocumentChunk]
  Input: Raw text, source identifier
  Output: List of DocumentChunk objects
  Logic: Use text_splitter with configured parameters
  
- process_pdf(pdf_path: str) -> List[DocumentChunk]
  Input: PDF path
  Output: List of chunks ready for embedding
  Logic: load_pdf() → chunk_text()
```

**Data Class: DocumentChunk**
```python
Fields:
- content: str (chunk text)
- metadata: dict (source, chunk_index)
- chunk_id: int (unique identifier)
```

**Algorithm: Recursive Text Splitting**
```
1. Try splitting by "\n\n" (paragraphs)
2. If chunks too large, split by "\n" (lines)
3. If still too large, split by ". " (sentences)
4. If still too large, split by " " (words)
5. Last resort: split by character
6. Ensure overlap between consecutive chunks
```

**Error Handling:**
- FileNotFoundError: Invalid PDF path
- PdfReadError: Corrupted PDF
- EmptyTextError: No extractable text

---

### 1.2 Embedding Module

**File:** `src/vector_store.py`

**Class: EmbeddingManager**

```python
Attributes:
- model: SentenceTransformer (all-MiniLM-L6-v2)

Methods:
- embed_text(text: str) -> List[float]
  Input: Single text string
  Output: 384-dimensional vector
  Logic: model.encode(text).tolist()
  
- embed_batch(texts: List[str]) -> List[List[float]]
  Input: List of texts
  Output: List of vectors
  Logic: Batch encoding for efficiency
  Optimization: Process 100 texts at once
```

**Embedding Pipeline:**
```
Text → Tokenization → Model Forward Pass → Pooling → Normalization → Vector
```

**Performance:**
- Single text: ~10ms
- Batch of 100: ~500ms
- GPU acceleration: 5x faster

---

### 1.3 Vector Storage Module

**File:** `src/vector_store.py`

**Class: VectorStore**

```python
Attributes:
- client: chromadb.PersistentClient
- collection: chromadb.Collection
- embedding_manager: EmbeddingManager

Methods:
- add_documents(chunks: List[DocumentChunk]) -> None
  Input: List of document chunks
  Output: None (side effect: DB insertion)
  Logic:
    1. Extract texts from chunks
    2. Generate embeddings in batch
    3. Insert into ChromaDB with metadata
  
- search(query: str, top_k: int) -> Tuple[List[str], List[float]]
  Input: Query string, number of results
  Output: (documents, similarity_scores)
  Logic:
    1. Embed query
    2. Perform cosine similarity search
    3. Return top-k results with scores
  
- clear() -> None
  Input: None
  Output: None
  Logic: Delete collection (for testing)
```

**ChromaDB Schema:**
```
Collection: customer_support
├── Embeddings: List[List[float]] (384-dim vectors)
├── Documents: List[str] (chunk text)
├── Metadatas: List[dict] (source, chunk_index)
└── IDs: List[str] (chunk_0, chunk_1, ...)

Index: HNSW (Hierarchical Navigable Small World)
Distance: Cosine similarity
```

**Search Algorithm:**
```
1. Query embedding: q
2. For each stored vector v:
   similarity = cosine(q, v) = (q · v) / (||q|| * ||v||)
3. Sort by similarity (descending)
4. Return top-k results
```

**Optimization:**
- HNSW index: O(log n) search time
- Batch insertions: 10x faster than individual
- Persistent storage: No re-indexing on restart

---

### 1.4 LLM Interface Module

**File:** `src/llm_interface.py`

**Class: LLMInterface**

```python
Attributes:
- client: OpenAI client
- model: str (gpt-3.5-turbo)

Methods:
- generate_response(query: str, context: List[str]) -> str
  Input: User query, retrieved context chunks
  Output: Generated answer
  Logic:
    1. Format context into prompt
    2. Create system + user messages
    3. Call OpenAI API
    4. Extract response text
  
- classify_intent(query: str) -> dict
  Input: User query
  Output: {intent, confidence, requires_human}
  Logic:
    1. Create classification prompt
    2. Request JSON response
    3. Parse and return structured data
```

**Prompt Template: Response Generation**
```
You are a customer support assistant. Answer based on context.

Context:
Context 1: [chunk 1]
Context 2: [chunk 2]
Context 3: [chunk 3]

User Question: [query]

Instructions:
- Answer based only on context
- Be concise and helpful
- If no answer in context, say "I don't have enough information"

Answer:
```

**Prompt Template: Intent Classification**
```
Classify the following customer query:

Query: [query]

Respond with JSON:
{
  "intent": "simple_question|complex_question|complaint|technical_issue",
  "confidence": 0.0-1.0,
  "requires_human": true|false
}
```

**API Configuration:**
- Temperature: 0.3 (focused, deterministic)
- Max tokens: 500 (concise responses)
- Timeout: 30 seconds
- Retry: 3 attempts with exponential backoff

---

### 1.5 HITL Module

**File:** `src/hitl_manager.py`

**Class: HITLManager**

```python
Attributes:
- pending_tickets: dict[str, EscalationTicket]
- resolved_tickets: dict[str, EscalationTicket]

Methods:
- should_escalate(query, intent_data, retrieval_confidence, threshold) -> (bool, str)
  Input: Query details, confidence scores
  Output: (should_escalate, reason)
  Logic: Check multiple escalation criteria
  
- create_ticket(query, context, reason) -> EscalationTicket
  Input: Query info, escalation reason
  Output: New ticket object
  Logic: Generate unique ID, store in pending
  
- resolve_ticket(ticket_id, human_response) -> None
  Input: Ticket ID, human's answer
  Output: None
  Logic: Move from pending to resolved
  
- get_pending_tickets() -> List[EscalationTicket]
  Input: None
  Output: All pending tickets
  
- save_tickets(filepath) -> None
  Input: File path
  Output: None
  Logic: Serialize tickets to JSON
```

**Data Class: EscalationTicket**
```python
Fields:
- ticket_id: str (TICKET_YYYYMMDDHHMMSS)
- query: str (user's question)
- context: list (retrieved chunks)
- reason: str (why escalated)
- timestamp: datetime
- status: str (pending|resolved)
- human_response: Optional[str]
```

**Escalation Logic:**
```python
def should_escalate(query, intent_data, retrieval_confidence, threshold):
    # Rule 1: Explicit human request
    if intent_data.get("requires_human"):
        return True, "Human intervention requested"
    
    # Rule 2: Low retrieval confidence
    if retrieval_confidence < threshold:
        return True, f"Low confidence: {retrieval_confidence}"
    
    # Rule 3: Sensitive intent
    if intent_data.get("intent") in ["complaint", "technical_issue"]:
        return True, f"Sensitive: {intent_data['intent']}"
    
    # Rule 4: Low intent confidence
    if intent_data.get("confidence", 1.0) < 0.6:
        return True, f"Uncertain intent: {intent_data['confidence']}"
    
    return False, ""
```

---

### 1.6 Workflow Module

**File:** `src/workflow.py`

**Class: RAGWorkflow**

```python
Attributes:
- vector_store: VectorStore
- llm: LLMInterface
- hitl: HITLManager
- graph: CompiledGraph

Methods:
- _build_graph() -> CompiledGraph
  Logic: Define nodes, edges, conditional routing
  
- classify_intent_node(state) -> GraphState
  Logic: Call LLM to classify query intent
  
- retrieve_context_node(state) -> GraphState
  Logic: Search vector store for relevant chunks
  
- should_escalate(state) -> str
  Logic: Decide routing path (escalate|continue)
  
- generate_response_node(state) -> GraphState
  Logic: Generate answer using LLM + context
  
- escalate_node(state) -> GraphState
  Logic: Create escalation ticket
  
- run(query) -> dict
  Logic: Execute graph with initial state
```

---

## 2. DATA STRUCTURES

### 2.1 Document Representation

**Raw Document:**
```python
{
    "path": str,
    "text": str,
    "pages": int,
    "size_bytes": int
}
```

**Processed Document:**
```python
{
    "chunks": List[DocumentChunk],
    "total_chunks": int,
    "source": str
}
```

### 2.2 Chunk Format

```python
DocumentChunk:
    content: str          # "Our product offers..."
    metadata: {
        "source": str,    # "data/kb.pdf"
        "chunk_index": int # 42
    }
    chunk_id: int         # 42
```

### 2.3 Embedding Structure

```python
Embedding:
    vector: List[float]   # [0.123, -0.456, ..., 0.789]
    dimension: int        # 384
    model: str            # "all-MiniLM-L6-v2"
```

### 2.4 Query-Response Schema

**Request:**
```python
{
    "query": str,         # "How do I reset my password?"
    "user_id": str,       # Optional
    "session_id": str     # Optional
}
```

**Response:**
```python
{
    "query": str,
    "response": str,
    "escalated": bool,
    "ticket_id": str,     # If escalated
    "intent": str,
    "confidence": float,
    "sources": List[str]  # Chunk IDs used
}
```

### 2.5 Graph State Object

```python
GraphState (TypedDict):
    query: str                    # User's question
    intent_data: dict             # Classification result
    retrieved_docs: List[str]     # Context chunks
    retrieval_scores: List[float] # Similarity scores
    response: str                 # Final answer
    escalated: bool               # Escalation flag
    escalation_reason: str        # Why escalated
    ticket_id: str                # Ticket ID if escalated
```

---

## 3. WORKFLOW DESIGN (LANGGRAPH)

### 3.1 Graph Structure

```
START
  │
  ▼
┌─────────────────┐
│ classify_intent │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ retrieve_context│
└────────┬────────┘
         │
         ▼
    [DECISION]
    /        \
   /          \
  ▼            ▼
escalate    generate
to_human    response
  │            │
  ▼            ▼
 END          END
```

### 3.2 Node Definitions

**Node 1: classify_intent**
```python
Input: GraphState with query
Process:
  1. Call llm.classify_intent(query)
  2. Parse JSON response
  3. Update state.intent_data
Output: GraphState with intent_data populated
Side effects: None
Error handling: Default to "simple_question" on failure
```

**Node 2: retrieve_context**
```python
Input: GraphState with query
Process:
  1. Call vector_store.search(query, top_k=3)
  2. Get documents and scores
  3. Update state.retrieved_docs and state.retrieval_scores
Output: GraphState with context
Side effects: None
Error handling: Return empty list on failure
```

**Node 3: generate_response**
```python
Input: GraphState with query + context
Process:
  1. Call llm.generate_response(query, retrieved_docs)
  2. Update state.response
  3. Set state.escalated = False
Output: GraphState with response
Side effects: None
Error handling: Return error message on API failure
```

**Node 4: escalate_to_human**
```python
Input: GraphState with query + context + reason
Process:
  1. Call hitl.create_ticket(query, context, reason)
  2. Update state.ticket_id
  3. Set state.escalated = True
  4. Create escalation message
Output: GraphState with ticket info
Side effects: Ticket stored in HITL manager
Error handling: Log error, still create ticket
```

### 3.3 Edge Definitions

**Unconditional Edges:**
- START → classify_intent
- classify_intent → retrieve_context
- generate_response → END
- escalate_to_human → END

**Conditional Edge:**
- retrieve_context → [should_escalate decision]
  - If escalate: → escalate_to_human
  - If continue: → generate_response

### 3.4 State Transitions

**Initial State:**
```python
{
    "query": "user input",
    "intent_data": {},
    "retrieved_docs": [],
    "retrieval_scores": [],
    "response": "",
    "escalated": False,
    "escalation_reason": "",
    "ticket_id": ""
}
```

**After classify_intent:**
```python
{
    "query": "user input",
    "intent_data": {
        "intent": "simple_question",
        "confidence": 0.9,
        "requires_human": False
    },
    "retrieved_docs": [],
    ...
}
```

**After retrieve_context:**
```python
{
    ...
    "retrieved_docs": ["chunk1", "chunk2", "chunk3"],
    "retrieval_scores": [0.15, 0.23, 0.31],
    ...
}
```

**Final State (AI Response):**
```python
{
    ...
    "response": "To reset your password, click...",
    "escalated": False,
    ...
}
```

**Final State (Escalated):**
```python
{
    ...
    "response": "Your query has been escalated...",
    "escalated": True,
    "escalation_reason": "Low confidence: 0.45",
    "ticket_id": "TICKET_20240115123045"
}
```

---

## 4. CONDITIONAL ROUTING LOGIC

### 4.1 Decision Function

```python
def should_escalate(state: GraphState) -> str:
    # Calculate average retrieval confidence
    avg_score = sum(state["retrieval_scores"]) / len(state["retrieval_scores"])
    confidence = 1 - avg_score  # Convert distance to confidence
    
    # Check escalation criteria
    should_esc, reason = hitl.should_escalate(
        query=state["query"],
        intent_data=state["intent_data"],
        retrieval_confidence=confidence,
        threshold=Config.CONFIDENCE_THRESHOLD
    )
    
    if should_esc:
        state["escalation_reason"] = reason
        return "escalate"
    
    return "continue"
```

### 4.2 Escalation Criteria

**Criterion 1: Explicit Human Request**
```python
if intent_data.get("requires_human") == True:
    escalate()
```
Example: "I want to speak to a human"

**Criterion 2: Low Retrieval Confidence**
```python
if retrieval_confidence < 0.7:
    escalate()
```
Calculation: confidence = 1 - avg_distance
- Distance 0.0 = perfect match (confidence 1.0)
- Distance 0.5 = moderate match (confidence 0.5)
- Distance 1.0 = no match (confidence 0.0)

**Criterion 3: Sensitive Intent**
```python
if intent in ["complaint", "technical_issue"]:
    escalate()
```
Rationale: These require empathy and expertise

**Criterion 4: Low Intent Confidence**
```python
if intent_confidence < 0.6:
    escalate()
```
Rationale: Uncertain classification = risky to auto-respond

### 4.3 Answer Generation Criteria

**Proceed with AI if:**
- Retrieval confidence ≥ 0.7
- Intent confidence ≥ 0.6
- Intent is "simple_question" or "complex_question"
- No explicit human request

**Quality Checks:**
- Response length > 10 characters
- Response doesn't contain "I don't know" (unless appropriate)
- Context relevance score > threshold

---

## 5. HITL DESIGN

### 5.1 Escalation Trigger Points

**Trigger Point 1: After Retrieval**
```
retrieve_context → calculate_confidence → check_threshold → escalate?
```

**Trigger Point 2: After Intent Classification**
```
classify_intent → check_sensitive_intent → escalate?
```

**Trigger Point 3: User Request**
```
query contains ["human", "agent", "person"] → escalate
```

### 5.2 Escalation Workflow

```
1. Detect escalation condition
2. Create EscalationTicket
   - Generate unique ID
   - Store query + context
   - Record reason
   - Set timestamp
3. Add to pending_tickets queue
4. Return escalation message to user
5. Notify human agent (future: email/Slack)
```

### 5.3 Human Response Integration

**Process:**
```
1. Human agent views pending tickets
2. Agent reviews query + context
3. Agent provides response
4. System calls resolve_ticket(ticket_id, response)
5. Ticket moved to resolved_tickets
6. Response sent to user
7. (Future) System learns from human response
```

**Data Flow:**
```
User → System → [Escalation] → Ticket Queue → Human Agent
                                                     ↓
User ← System ← [Resolution] ← Ticket Update ← Human Agent
```

### 5.4 Ticket Management

**Ticket States:**
- pending: Awaiting human response
- resolved: Human has responded
- archived: Older than 30 days

**Ticket Priority:**
- High: Complaints, technical issues
- Medium: Complex questions
- Low: Low confidence queries

**SLA Targets:**
- High priority: 1 hour
- Medium priority: 4 hours
- Low priority: 24 hours

---

## 6. API / INTERFACE DESIGN

### 6.1 CLI Interface

**Commands:**

1. **Ingest PDF**
```bash
python main.py ingest <pdf_path>
```
Input: Path to PDF file
Output: Confirmation message + chunk count

2. **Query**
```bash
python main.py
> Your question here
```
Input: Natural language question
Output: AI response or escalation notice

3. **View Tickets**
```bash
> tickets
```
Output: List of pending escalations

4. **Resolve Ticket**
```bash
> resolve TICKET_ID response text here
```
Input: Ticket ID + human response
Output: Confirmation

### 6.2 Programmatic API (Future)

**Endpoint: POST /ingest**
```python
Request:
{
    "pdf_path": str,
    "collection_name": str (optional)
}

Response:
{
    "status": "success",
    "chunks_created": int,
    "processing_time": float
}
```

**Endpoint: POST /query**
```python
Request:
{
    "query": str,
    "user_id": str (optional),
    "session_id": str (optional)
}

Response:
{
    "query": str,
    "response": str,
    "escalated": bool,
    "ticket_id": str (if escalated),
    "intent": str,
    "confidence": float,
    "processing_time": float
}
```

**Endpoint: GET /tickets**
```python
Response:
{
    "pending": List[EscalationTicket],
    "count": int
}
```

**Endpoint: POST /tickets/{ticket_id}/resolve**
```python
Request:
{
    "response": str
}

Response:
{
    "status": "resolved",
    "ticket_id": str
}
```

### 6.3 Interaction Flow

**Scenario 1: Successful AI Response**
```
User: "How do I reset my password?"
  ↓
System: [classify] → simple_question
  ↓
System: [retrieve] → 3 relevant chunks (confidence: 0.85)
  ↓
System: [generate] → "To reset your password, click..."
  ↓
User: Receives answer
```

**Scenario 2: Escalation**
```
User: "I'm very unhappy with your service!"
  ↓
System: [classify] → complaint (confidence: 0.95)
  ↓
System: [retrieve] → 3 chunks (confidence: 0.75)
  ↓
System: [escalate] → Create TICKET_123
  ↓
User: "Your query has been escalated. Ticket: TICKET_123"
  ↓
Human Agent: Reviews ticket
  ↓
Human Agent: Provides response
  ↓
System: Resolves ticket
  ↓
User: Receives human response
```

---

## 7. ERROR HANDLING

### 7.1 Missing Data Errors

**Error: PDF Not Found**
```python
try:
    text = load_pdf(path)
except FileNotFoundError:
    log_error(f"PDF not found: {path}")
    return {"error": "File not found"}
```

**Error: Empty PDF**
```python
if not text or len(text.strip()) == 0:
    log_warning(f"Empty PDF: {path}")
    return {"error": "No extractable text"}
```

### 7.2 No Relevant Chunks Found

**Error: Empty Search Results**
```python
docs, scores = vector_store.search(query)
if not docs:
    # Escalate due to no context
    return escalate_to_human(
        query=query,
        context=[],
        reason="No relevant information found"
    )
```

**Error: Low Quality Results**
```python
if all(score > 0.8 for score in scores):  # High distance = low similarity
    # Results too dissimilar
    return escalate_to_human(
        query=query,
        context=docs,
        reason="Retrieved context not relevant"
    )
```

### 7.3 LLM Failure

**Error: API Timeout**
```python
try:
    response = llm.generate_response(query, context)
except Timeout:
    log_error("LLM API timeout")
    retry_count += 1
    if retry_count < 3:
        time.sleep(2 ** retry_count)  # Exponential backoff
        retry()
    else:
        return {"error": "Service temporarily unavailable"}
```

**Error: API Rate Limit**
```python
except RateLimitError:
    log_warning("Rate limit hit")
    return {
        "response": "High traffic. Please try again in a moment.",
        "escalated": False
    }
```

**Error: Invalid API Key**
```python
except AuthenticationError:
    log_critical("Invalid OpenAI API key")
    return {"error": "Configuration error. Contact administrator."}
```

### 7.4 ChromaDB Errors

**Error: Collection Not Found**
```python
try:
    collection = client.get_collection(name)
except ValueError:
    log_info(f"Collection {name} not found, creating...")
    collection = client.create_collection(name)
```

**Error: Disk Space Full**
```python
except IOError as e:
    if "No space left" in str(e):
        log_critical("Disk space full")
        # Trigger cleanup or alert
        return {"error": "Storage full"}
```

### 7.5 General Error Handling Strategy

**Principle: Fail Gracefully**
```python
def safe_execute(func, fallback):
    try:
        return func()
    except Exception as e:
        log_error(f"Error in {func.__name__}: {e}")
        return fallback
```

**Logging Levels:**
- DEBUG: Detailed execution trace
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failed operations
- CRITICAL: System-level failures

**Error Response Format:**
```python
{
    "success": bool,
    "data": dict (if success),
    "error": {
        "code": str,
        "message": str,
        "details": dict
    } (if failure)
}
```

---

## 8. PERFORMANCE OPTIMIZATIONS

### 8.1 Caching Strategy

**Query Cache:**
```python
cache = {}  # In-memory cache

def query_with_cache(query):
    cache_key = hash(query.lower().strip())
    if cache_key in cache:
        return cache[cache_key]
    
    result = execute_query(query)
    cache[cache_key] = result
    return result
```

**Embedding Cache:**
```python
# Cache embeddings for common queries
embedding_cache = {}

def embed_with_cache(text):
    if text in embedding_cache:
        return embedding_cache[text]
    
    embedding = model.encode(text)
    embedding_cache[text] = embedding
    return embedding
```

### 8.2 Batch Processing

**Batch Embedding:**
```python
# Instead of:
for chunk in chunks:
    embedding = embed(chunk)
    store(embedding)

# Do:
embeddings = embed_batch(chunks)  # 10x faster
store_batch(embeddings)
```

### 8.3 Async Operations (Future)

```python
async def query_async(query):
    intent_task = asyncio.create_task(classify_intent(query))
    retrieval_task = asyncio.create_task(retrieve_context(query))
    
    intent, context = await asyncio.gather(intent_task, retrieval_task)
    
    response = await generate_response(query, context)
    return response
```

---

## 9. TESTING STRATEGY

### 9.1 Unit Tests

**Test: Document Chunking**
```python
def test_chunking():
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
    text = "A" * 500
    chunks = processor.chunk_text(text)
    
    assert len(chunks) > 1
    assert all(len(c.content) <= 120 for c in chunks)
    # Check overlap
    assert chunks[0].content[-20:] == chunks[1].content[:20]
```

**Test: Escalation Logic**
```python
def test_escalation():
    hitl = HITLManager()
    
    # Test low confidence
    should_esc, reason = hitl.should_escalate(
        query="test",
        intent_data={"intent": "simple", "confidence": 0.9},
        retrieval_confidence=0.5,
        threshold=0.7
    )
    assert should_esc == True
    assert "Low confidence" in reason
```

### 9.2 Integration Tests

**Test: End-to-End Query**
```python
def test_e2e_query():
    rag = RAGSystem()
    rag.ingest_pdf("test_data/sample.pdf")
    
    result = rag.query("What is the product price?")
    
    assert result["response"] != ""
    assert result["escalated"] in [True, False]
```

### 9.3 Performance Tests

**Test: Query Latency**
```python
def test_latency():
    rag = RAGSystem()
    
    start = time.time()
    result = rag.query("Test query")
    end = time.time()
    
    latency = end - start
    assert latency < 1.0  # Must respond in <1 second
```

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Author:** RAG System Implementation Team
