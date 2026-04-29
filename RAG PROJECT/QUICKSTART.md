# QUICK START GUIDE
## Get Your RAG System Running in 5 Minutes

---

## ⚡ Prerequisites
- Python 3.9+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

---

## 🚀 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key (30 sec)
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Ingest Knowledge Base (1 min)
```bash
python main.py ingest data/sample_knowledge_base.txt
```

Expected output:
```
Processing PDF: data/sample_knowledge_base.txt
Created 45 chunks
Documents indexed successfully
```

### Step 4: Start Chatting! (2 min)
```bash
python main.py
```

---

## 💬 Try These Queries

### Simple Question (AI handles)
```
You: What is the price of CloudSync Pro?
Assistant: CloudSync Pro costs $9.99/month and includes 1TB storage, automatic backup, and file sharing capabilities.
```

### Password Reset (AI handles)
```
You: How do I reset my password?
Assistant: To reset your password, follow these steps:
1. Click the "Forgot Password" link on the login page
2. Enter your email address
3. Check your email for the reset link
4. Click the link and create a new password
```

### Complaint (Escalates to human)
```
You: I'm very unhappy with your service!
Assistant: Your query has been escalated to a human agent. Ticket ID: TICKET_20240115123045
Reason: Sensitive intent: complaint
```

### Technical Issue (Escalates to human)
```
You: My app keeps crashing with error 500
Assistant: Your query has been escalated to a human agent. Ticket ID: TICKET_20240115123046
Reason: Sensitive intent: technical_issue
```

---

## 🎫 Managing Tickets

### View Pending Tickets
```
You: tickets

[TICKET_20240115123045]
Query: I'm very unhappy with your service!
Reason: Sensitive intent: complaint
Time: 2024-01-15 12:30:45

[TICKET_20240115123046]
Query: My app keeps crashing with error 500
Reason: Sensitive intent: technical_issue
Time: 2024-01-15 12:31:20
```

### Resolve a Ticket
```
You: resolve TICKET_20240115123045 I sincerely apologize for the inconvenience. Let me help you resolve this issue immediately...

Ticket TICKET_20240115123045 resolved.
```

---

## 🔧 Common Commands

| Command | Description |
|---------|-------------|
| `python main.py ingest <path>` | Ingest a PDF/text file |
| `python main.py` | Start interactive chat |
| `tickets` | View pending escalations |
| `resolve <id> <response>` | Resolve a ticket |
| `exit` | Quit the application |

---

## 📊 What's Happening Behind the Scenes?

When you ask a question:

1. **Intent Classification** (200ms)
   - LLM analyzes your query
   - Determines: simple/complex/complaint/technical

2. **Context Retrieval** (50ms)
   - Searches vector database
   - Finds top-3 relevant chunks

3. **Routing Decision** (10ms)
   - Checks confidence scores
   - Decides: AI or Human

4. **Response Generation** (500ms)
   - If AI: LLM generates answer
   - If Human: Creates escalation ticket

**Total Time: ~760ms** ⚡

---

## 🎯 Understanding Escalations

Your query is escalated to a human if:

❌ **Low Confidence**: Retrieved information isn't relevant enough  
❌ **Complaint**: Negative sentiment detected  
❌ **Technical Issue**: Requires expert troubleshooting  
❌ **Uncertain Intent**: System isn't sure how to classify  
❌ **Explicit Request**: You ask for a human agent  

Otherwise, AI handles it! ✅

---

## 📁 Project Structure

```
RAG PROJECT/
├── src/              # Core system code
├── docs/             # Design documents (HLD, LLD, Technical)
├── data/             # Knowledge base files
├── tests/            # Unit tests
├── main.py           # CLI interface
└── requirements.txt  # Dependencies
```

---

## 🔍 Explore Further

### Read the Documentation
- **[README.md](README.md)**: Complete project overview
- **[SETUP.md](SETUP.md)**: Detailed setup instructions
- **[docs/HLD.md](docs/HLD.md)**: High-level architecture
- **[docs/LLD.md](docs/LLD.md)**: Implementation details
- **[docs/Technical_Documentation.md](docs/Technical_Documentation.md)**: Full technical guide

### Run Tests
```bash
python -m pytest tests/test_rag.py -v
```

### Try Programmatic Usage
```bash
python example_usage.py
```

### Customize
Edit `.env` to adjust:
- Chunk size
- Confidence threshold
- LLM model
- Embedding model

---

## 🐛 Troubleshooting

### "No module named 'src'"
→ Make sure you're in the project root directory

### "OpenAI API key not found"
→ Check `.env` file exists and contains valid key

### "ChromaDB error"
→ Delete `chroma_db/` folder and re-ingest

### Slow first run
→ First run downloads embedding model (~80MB), subsequent runs are fast

---

## 💡 Tips

1. **Start Simple**: Try basic questions first
2. **Test Escalations**: Try complaints to see HITL in action
3. **Check Tickets**: Use `tickets` command to see escalations
4. **Customize Knowledge**: Add your own PDF files
5. **Tune Parameters**: Adjust `.env` for your use case

---

## 🎓 Next Steps

1. ✅ Run the quick start (you're here!)
2. 📖 Read the full documentation
3. 🔧 Customize for your use case
4. 🧪 Run tests and experiments
5. 🚀 Deploy to production

---

## 📞 Need Help?

- Check [SETUP.md](SETUP.md) for detailed instructions
- Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for complete overview
- Read technical docs in `docs/` folder
- Run tests to verify setup

---

**You're all set! Start asking questions and see RAG in action! 🎉**
