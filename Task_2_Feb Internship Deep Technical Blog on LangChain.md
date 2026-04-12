# 🚀 LangChain Deep Dive: Building Real-World LLM Applications

This project is part of my **Data Science Internship – February 2026**, where I explored LangChain and built modular LLM-powered applications.

📖 **Read Full Blog:**  
https://medium.com/p/b31ead34237c

---

1. Introduction to LangChain
Large Language Models (LLMs) like GPT are incredibly powerful — but in isolation, they are limited.

A simple API call:

response = llm.invoke(“What is AI?”)

…gives you an answer, but that’s where it ends.

There is:

No memory of past interactions
No connection to external data
No ability to perform actions
No structured workflow
This makes raw LLMs unsuitable for real-world applications.

What is LangChain?
LangChain is an open-source framework that enables developers to build LLM-powered applications using modular components such as prompts, chains, memory, and agents.

It solves three critical problems:

1. Orchestration
Managing multiple steps (LLM calls, tools, logic) in a pipeline.

2. Chaining
Passing outputs from one step to another in a structured way.

3. Tool Integration
Connecting LLMs with:

APIs
Databases
Search engines
Custom Python functions
👉 In short:

LangChain transforms LLMs from simple responders into intelligent systems.

2. Core Components of LangChain
2.1 LLMs and Chat Models
Concept
LLMs generate text based on input. ChatModels work with structured messages.

Why it exists
To standardize different providers under one interface.

Code Example
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(model=”gpt-4o-mini”, temperature=0.7)

messages = [
SystemMessage(content=”You are a helpful assistant.”),
HumanMessage(content=”Explain Python in 2 lines.”)
]

response = llm.invoke(messages)
print(response.content)

Insight
LangChain internally converts messages into API format and returns structured responses.

2.2 Prompt Templates
Concept
Dynamic prompts with variables.

Why it exists
Hardcoded prompts are not scalable or reusable.

Code Example
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
(“system”, “You are an expert {role}.”),
(“human”, “Explain: {topic}”)
])

messages = prompt.invoke({
“role”: “data scientist”,
“topic”: “overfitting”
})

Insight
Prompt templates make prompts reusable and testable.

2.3 Chains (LCEL)
Concept
Combine multiple steps into a pipeline.

Why it exists
To avoid writing manual glue code.

Code Example
from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()
chain = prompt | llm | parser
result = chain.invoke({
    "role": "teacher",
    "topic": "machine learning"
})
print(result)
🧠 Insight

LCEL (|) creates a sequence where each step feeds the next.
2.4 Memory
Concept
Stores conversation history.

Why it exists
LLMs are stateless.

Code Example
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain

memory = ConversationBufferWindowMemory(k=2)

conversation = ConversationChain(
llm=llm,
memory=memory
)

conversation.predict(input=”My name is Rahul”)
response = conversation.predict(input=”What is my name?”)
print(response)

Insight
Memory injects past interactions into future prompts.

2.5 Agents
Concept
Dynamic decision-making systems.

Why it exists
Fixed chains cannot handle complex tasks.

Code Example
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool

@tool
def calculator(expr: str) -> str:
return str(eval(expr))

agent = create_tool_calling_agent(llm, [calculator])
executor = AgentExecutor(agent=agent, tools=[calculator])

result = executor.invoke({“input”: “What is 25 * 4?”})
print(result[“output”])

Insight
Agents decide:

Which tool to use
When to stop
2.6 Tools
Concept
External capabilities for LLMs.

Why it exists
LLMs cannot access real-world data.

Code Example
from langchain_core.tools import tool

Become a Medium member
@tool
def get_weather(city: str) -> str:
return f”Weather in {city} is sunny”

print(get_weather.invoke(“Pune”))

2.7 Document Loaders
Concept
Load external data into LangChain.

Why it exists
To work with PDFs, web data, etc.

Code Example
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(“sample.pdf”)
docs = loader.load()

print(docs[0].page_content[:100])

2.8 Vector Stores
Concept
Store embeddings for semantic search.

Why it exists
LLMs cannot process large documents directly.

Code Example
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())

results = vectorstore.similarity_search(“What is AI?”, k=2)

for r in results:
print(r.page_content[:100])

3. Architecture Explanation (MANDATORY DIAGRAM)
Pipeline Flow
User Input
   ↓
Prompt Template
   ↓
LLM / Chat Model
   ↓
Chain (LCEL)
   ↓
Agent + Tools
   ↓
Final Output
Supporting Systems
Memory → conversation context
Vector Store → knowledge retrieval
This architecture ensures:

Context-aware responses
External knowledge integration
Dynamic execution
Press enter or click to view image in full size
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/bcb2eb8c-feea-4c2a-8818-78664167a964" />
4. Hands-on Code Implementation
Basic LLM Call
llm.invoke(“Explain AI”)

Prompt Template + Chain
chain = prompt | llm | StrOutputParser()
print(chain.invoke({"role": "engineer", "topic": "AI"}))
Memory Example

conversation.predict(input=”I love Python”)
conversation.predict(input=”What do I love?”)

Agent with Tool
executor.invoke({"input": "Calculate 100/5"})
Mini RAG Example
retriever = vectorstore.as_retriever()
rag_chain = (
    {"context": retriever, "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)
print(rag_chain.invoke("Explain topic"))
5. Real-World Use Cases
1. Customer Support Bot
Problem: Handling thousands of queries manually.

Solution:

Use Document Loaders + Vector Store
Add Memory for conversation
Use Agent for dynamic queries
Components:
RAG + Memory + Tools

2. Automated Code Review
Problem: Manual PR review delays.

Solution:

Load code using GitLoader
Run multiple chains (security, performance)
Generate structured report
3. Research Paper Analyzer
Problem: Reading hundreds of papers is time-consuming.

Solution:

Load PDFs
Store in vector DB
Query using RAG
6. Advantages and Limitations
Advantages
Modular design
Fast prototyping
Easy integration
Scalable pipelines
Limitations
High latency (agents)
Complex debugging
Increased cost
Frequent API updates
When NOT to Use
Simple one-step tasks
Low-latency systems
Small applications
7. Conclusion
LangChain is more than a framework — it is a design paradigm for building AI systems.

Key Takeaways
LLMs alone are not enough
Modular pipelines are essential
RAG is critical for real-world apps
Agents enable intelligent decision-making
Future Scope
LangGraph (graph-based workflows)
Multi-agent systems
Autonomous AI pipelines
5. Real-World Use Cases
1. Customer Support Bot
Problem: Handling thousands of queries manually.

Solution:

Use Document Loaders + Vector Store
Add Memory for conversation
Use Agent for dynamic queries
Components:
RAG + Memory + Tools

2. Automated Code Review
Problem: Manual PR review delays.

Solution:

Load code using GitLoader
Run multiple chains (security, performance)
Generate structured report
3. Research Paper Analyzer
Problem: Reading hundreds of papers is time-consuming.

Solution:

Load PDFs
Store in vector DB
Query using RAG
6. Advantages and Limitations
Advantages
Modular design
Fast prototyping
Easy integration
Scalable pipelines
Limitations
High latency (agents)
Complex debugging
Increased cost
Frequent API updates
When NOT to Use
Simple one-step tasks
Low-latency systems
Small applications

7. Conclusion
LangChain is more than a framework — it is a design paradigm for building AI systems.

Key Takeaways
LLMs alone are not enough
Modular pipelines are essential
RAG is critical for real-world apps
Agents enable intelligent decision-making
Future Scope
LangGraph (graph-based workflows)
Multi-agent systems
Autonomous AI pipelines
