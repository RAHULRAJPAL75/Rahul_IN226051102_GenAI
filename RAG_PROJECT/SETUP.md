# SETUP INSTRUCTIONS

## Step-by-Step Setup Guide

### 1. Environment Setup

**Install Python 3.9 or higher**
```bash
python --version  # Should be 3.9+
```

**Create virtual environment (recommended)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- langchain & langchain-community
- langgraph
- chromadb
- pypdf
- sentence-transformers
- openai
- python-dotenv
- fastapi & uvicorn
- pydantic

### 3. Configure Environment

**Create .env file**
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

**Edit .env file and add your OpenAI API key**
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 4. Prepare Knowledge Base

**Option A: Use sample data**
The project includes `data/sample_knowledge_base.txt` with sample customer support content.

**Option B: Add your own PDF**
Place your PDF file in the `data/` folder.

### 5. Ingest Documents

```bash
python main.py ingest data/sample_knowledge_base.txt
```

You should see:
```
Processing PDF: data/sample_knowledge_base.txt
Created X chunks
Documents indexed successfully
```

### 6. Run the Assistant

```bash
python main.py
```

You'll see:
```
============================================================
RAG-Based Customer Support Assistant
============================================================

Commands:
  - Type your question
  - 'tickets' to view pending escalations
  - 'resolve <ticket_id> <response>' to resolve a ticket
  - 'exit' to quit

You: 
```

### 7. Test the System

**Test 1: Simple Question**
```
You: What is the price of CloudSync Pro?
Assistant: CloudSync Pro costs $9.99/month...
```

**Test 2: Escalation**
```
You: I'm very unhappy with your service!
Assistant: Your query has been escalated to a human agent. Ticket ID: TICKET_...
```

**Test 3: View Tickets**
```
You: tickets
[TICKET_20240115123045]
Query: I'm very unhappy with your service!
Reason: Sensitive intent: complaint
Time: 2024-01-15 12:30:45
```

**Test 4: Resolve Ticket**
```
You: resolve TICKET_20240115123045 I apologize for the inconvenience...
Ticket TICKET_20240115123045 resolved.
```

### 8. Run Tests (Optional)

```bash
python -m pytest tests/test_rag.py -v
```

---

## Troubleshooting

### Issue: "No module named 'src'"
**Solution**: Make sure you're in the project root directory.

### Issue: "OpenAI API key not found"
**Solution**: Check that `.env` file exists and contains valid API key.

### Issue: "ChromaDB error"
**Solution**: Delete `chroma_db/` folder and re-ingest documents.

### Issue: "PDF not found"
**Solution**: Check file path is correct. Use forward slashes or raw strings.

### Issue: "Slow embedding generation"
**Solution**: First run downloads the model (~80MB). Subsequent runs are fast.

---

## Configuration Options

### Adjust Chunk Size
In `.env`:
```env
CHUNK_SIZE=500      # Increase for more context
CHUNK_OVERLAP=50    # Increase to prevent boundary issues
```

### Change LLM Model
In `.env`:
```env
LLM_MODEL=gpt-4              # Better quality, higher cost
LLM_MODEL=gpt-3.5-turbo      # Good balance (default)
```

### Adjust Escalation Threshold
In `.env`:
```env
CONFIDENCE_THRESHOLD=0.7     # Lower = more escalations
CONFIDENCE_THRESHOLD=0.5     # Higher = fewer escalations
```

---

## Next Steps

1. **Customize Knowledge Base**: Add your own PDF documents
2. **Tune Parameters**: Adjust chunk size, threshold, etc.
3. **Extend Functionality**: Add new features (see roadmap)
4. **Deploy**: Set up production environment

---

## Support

If you encounter issues:
1. Check this guide
2. Review error messages
3. Check logs
4. Consult documentation in `docs/`
5. Open an issue on GitHub

---

**Happy Building! 🚀**
