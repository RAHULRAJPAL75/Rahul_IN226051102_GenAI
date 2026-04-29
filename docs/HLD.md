# HIGH-LEVEL DESIGN (HLD)
## RAG-Based Customer Support Assistant with LangGraph & HITL

---

## 1. SYSTEM OVERVIEW

### 1.1 Problem Definition
Customer support teams face challenges:
- High volume of repetitive queries
- Inconsistent response quality
- Slow response times
- Knowledge scattered across documents
- Human agents overwhelmed with simple questions

### 1.2 Solution
A Retrieval-Augmented Generation (RAG) system that:
- Automatically answers queries using a knowledge base
- Routes complex/sensitive issues to humans
- Maintains context and accuracy
- Scales efficiently with growing knowledge

### 1.3 Scope
**In Scope:**
- PDF document ingestion and processing
- Semantic search using embeddings
- LLM-powered response generation
- Graph-based workflow orchestration
- Intent classification and routing
- Human-in-the-Loop escalation
- CLI interface

**Out of Scope:**
- Multi-modal inputs (images, audio)
- Real-time chat UI (web interface)
- Multi-language support
- User authentication system

---

## 2. ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (CLI / API Layer)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG SYSTEM CORE                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              LANGGRAPH WORKFLOW ENGINE                   │  │
│  │                                                          │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────────┐     │  │
│  │  │ Classify │───▶│ Retrieve │───▶│   Generate   │     │  │
│  │  │  Intent  │    │ Context  │    │   Response   │     │  │
│  │  └──────────┘    └──────────┘    └──────────────┘     │  │
│  │                        │                               │  │
│  │                        │ (conditional routing)         │  │
│  │                        ▼                               │  │
│  │                  ┌──────────┐                          │  │
│  │                  │ Escalate │                          │  │
│  │                  │ to Human │                          │  │
│  │                  └──────────┘                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   LLM INTERFACE  │  │  VECTOR STORE    │  │  HITL MANAGER    │
│   (OpenAI API)   │  │   (ChromaDB)     │  │  (Escalation)    │
└──────────────────┘  └──────────────────┘  └──────────────────┘
                              ▲
                              │
                    ┌─────────┴─────────┐
                    │                   │
          ┌─────────▼────────┐  ┌──────▼──────────┐
          │ EMBEDDING MODEL  │  │  DOCUMENT       │
          │ (SentenceTransf) │  │  PROCESSOR      │
          └──────────────────┘  └─────────────────┘
                                        ▲
                                        │
                                ┌───────┴────────┐
                                │  PDF LOADER    │
                                │  & CHUNKER     │
                                └────────────────┘
```

---

## 3. COMPONENT DESCRIPTION

### 3.1 Document Loader
**Purpose:** Extract text from PDF files
**Technology:** PyPDF
**Input:** PDF file path
**Output:** Raw text string
**Key Features:**
- Page-by-page extraction
- Handles multi-page documents
- Error handling for corrupted PDFs

### 3.2 Chunking Strategy
**Purpose:** Split documents into manageable pieces
**Technology:** LangChain RecursiveCharacterTextSplitter
**Parameters:**
- Chunk size: 500 characters
- Overlap: 50 characters
- Separators: ["\n\n", "\n", ". ", " "]

**Rationale:**
- 500 chars balances context vs. precision
- 50 char overlap prevents context loss at boundaries
- Hierarchical separators preserve semantic units

### 3.3 Embedding Model
**Purpose:** Convert text to vector representations
**Technology:** SentenceTransformers (all-MiniLM-L6-v2)
**Specifications:**
- Dimension: 384
- Speed: ~2000 sentences/sec
- Quality: Optimized for semantic similarity

**Why this model:**
- Lightweight (80MB)
- Fast inference
- Good balance of speed/accuracy
- No API costs

### 3.4 Vector Store
**Purpose:** Store and retrieve embeddings
**Technology:** ChromaDB
**Features:**
- Persistent storage
- Cosine similarity search
- Metadata filtering
- HNSW indexing for speed

**Why ChromaDB:**
- Embedded database (no server needed)
- Python-native
- Excellent for prototypes and production
- Built-in persistence

### 3.5 Retriever
**Purpose:** Find relevant context for queries
**Method:** Semantic similarity search
**Parameters:**
- Top-k: 3 documents
- Distance metric: Cosine similarity
**Output:** Ranked list of relevant chunks + scores

### 3.6 LLM
**Purpose:** Generate natural language responses
**Technology:** OpenAI GPT-3.5-turbo
**Configuration:**
- Temperature: 0.3 (focused responses)
- Context window: 4096 tokens
- Role: Customer support assistant

**Why GPT-3.5:**
- Cost-effective
- Fast response times
- Good instruction following
- Reliable for production

### 3.7 Graph Workflow Engine
**Purpose:** Orchestrate processing pipeline
**Technology:** LangGraph
**Components:**
- State management
- Node execution
- Conditional routing
- Error handling

**Nodes:**
1. classify_intent: Analyze query type
2. retrieve_context: Fetch relevant docs
3. generate_response: Create answer
4. escalate_to_human: Create ticket

### 3.8 Routing Layer
**Purpose:** Decide processing path
**Logic:**
- Check intent classification
- Evaluate retrieval confidence
- Assess query complexity
- Route to AI or human

**Routing Criteria:**
- Confidence threshold: 0.7
- Intent types: simple/complex/complaint/technical
- Retrieval score analysis

### 3.9 HITL Module
**Purpose:** Manage human escalations
**Features:**
- Ticket creation
- Reason tracking
- Status management
- Resolution handling

**Escalation Triggers:**
- Low confidence (<0.7)
- Complaint intent
- Technical issues
- Explicit human request

---

## 4. DATA FLOW

### 4.1 Ingestion Flow
```
PDF File → Load Text → Split into Chunks → Generate Embeddings → Store in ChromaDB
```

**Steps:**
1. User provides PDF path
2. PyPDF extracts text
3. Text splitter creates chunks
4. Embedding model vectorizes chunks
5. ChromaDB stores vectors + metadata

### 4.2 Query Flow
```
User Query → Intent Classification → Context Retrieval → Routing Decision
                                                              ├─→ Generate Response → User
                                                              └─→ Escalate to Human → Ticket
```

**Steps:**
1. User submits question
2. LLM classifies intent
3. Vector store retrieves top-3 chunks
4. System calculates confidence
5. Router decides: AI or Human
6. If AI: LLM generates response
7. If Human: Create escalation ticket

---

## 5. TECHNOLOGY CHOICES

### 5.1 Why ChromaDB?
- **Embedded:** No separate server
- **Fast:** HNSW indexing
- **Persistent:** Data survives restarts
- **Simple API:** Easy integration
- **Metadata:** Rich filtering capabilities

**Alternatives considered:**
- Pinecone: Requires cloud, costs money
- Weaviate: Overkill for this scale
- FAISS: No persistence out-of-box

### 5.2 Why LangGraph?
- **Control:** Explicit workflow definition
- **Flexibility:** Conditional routing
- **State Management:** Clean data flow
- **Debugging:** Clear execution trace
- **Production-Ready:** Built for real systems

**Alternatives considered:**
- LangChain LCEL: Less control over routing
- Custom code: Reinventing the wheel
- Airflow: Too heavy for this use case

### 5.3 LLM Choice
**Primary:** OpenAI GPT-3.5-turbo
- Cost: $0.0015/1K tokens
- Speed: ~500ms response
- Quality: Excellent for support

**Fallback options:**
- GPT-4: Higher quality, 10x cost
- Claude: Good alternative
- Open-source: Llama 2 (self-hosted)

### 5.4 Additional Tools
- **LangChain:** Document processing utilities
- **SentenceTransformers:** Local embeddings
- **Pydantic:** Data validation
- **Python-dotenv:** Configuration management

---

## 6. SCALABILITY CONSIDERATIONS

### 6.1 Handling Large Documents
**Current Approach:**
- Chunk size: 500 chars
- Batch embedding: 100 chunks at a time

**Scaling Strategy:**
- Increase chunk size for dense docs
- Parallel processing for multiple PDFs
- Streaming ingestion for huge files

**Bottlenecks:**
- Embedding generation: ~1000 chunks/min
- ChromaDB insertion: ~5000 docs/sec

**Solutions:**
- GPU acceleration for embeddings
- Batch inserts to ChromaDB
- Async processing pipeline

### 6.2 Increasing Query Load
**Current Capacity:**
- ~10 queries/sec (limited by LLM API)
- ChromaDB: 1000s queries/sec

**Scaling Strategy:**
- Cache frequent queries
- Load balancing across API keys
- Rate limiting per user
- Queue system for high load

**Monitoring:**
- Query latency tracking
- API usage metrics
- Cache hit rates

### 6.3 Latency Concerns
**Current Latency:**
- Embedding: ~50ms
- Vector search: ~20ms
- LLM call: ~500ms
- Total: ~600ms

**Optimization:**
- Reduce top-k to 2 docs
- Use GPT-3.5-turbo-instruct (faster)
- Implement response streaming
- Pre-compute common queries

**Target:** <400ms for 95th percentile

### 6.4 Storage Growth
**Estimates:**
- 1000-page PDF → ~2000 chunks
- Each chunk: ~1KB metadata + 384-dim vector
- Storage: ~2MB per 1000 pages

**Scaling:**
- ChromaDB handles millions of vectors
- Disk space: 1GB = ~500 PDFs
- Compression for older data

---

## 7. SYSTEM CHARACTERISTICS

### 7.1 Performance
- Query response: <1 second
- Ingestion: ~1 minute per 100-page PDF
- Concurrent users: 10-50 (API limited)

### 7.2 Reliability
- Persistent storage (no data loss)
- Error handling at each layer
- Graceful degradation
- Retry logic for API calls

### 7.3 Security
- API keys in environment variables
- No PII in logs
- Secure vector storage
- Input sanitization

### 7.4 Maintainability
- Modular architecture
- Clear separation of concerns
- Comprehensive logging
- Unit tests for core components

---

## 8. DEPLOYMENT ARCHITECTURE

### 8.1 Development
```
Local Machine
├── Python 3.9+
├── ChromaDB (local)
├── OpenAI API (cloud)
└── CLI interface
```

### 8.2 Production (Future)
```
Cloud Infrastructure
├── API Server (FastAPI)
├── ChromaDB (persistent volume)
├── Redis (caching)
├── Load Balancer
└── Monitoring (Prometheus/Grafana)
```

---

## 9. SUCCESS METRICS

### 9.1 System Metrics
- Response accuracy: >85%
- Query latency: <1s
- System uptime: >99%
- Escalation rate: <20%

### 9.2 Business Metrics
- Queries resolved without human: >80%
- User satisfaction: >4/5
- Response time reduction: >50%
- Support cost reduction: >30%

---

## 10. RISK ANALYSIS

### 10.1 Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API downtime | High | Fallback to cached responses |
| Embedding quality | Medium | A/B test different models |
| ChromaDB corruption | High | Regular backups |
| High latency | Medium | Caching + optimization |

### 10.2 Business Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Incorrect answers | High | HITL for sensitive queries |
| API costs | Medium | Usage monitoring + limits |
| User adoption | Medium | Training + documentation |

---

## 11. FUTURE ENHANCEMENTS

### 11.1 Phase 2
- Web UI with real-time chat
- Multi-document support
- Conversation memory
- Analytics dashboard

### 11.2 Phase 3
- Multi-language support
- Voice interface
- Integration with ticketing systems
- Fine-tuned domain-specific LLM

### 11.3 Phase 4
- Feedback loop for continuous learning
- A/B testing framework
- Advanced analytics
- Mobile app

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Author:** RAG System Design Team
