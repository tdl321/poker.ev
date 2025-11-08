# LangChain & LangGraph: RAG-Powered, Prompt-Engineered LLM Agents

## Comprehensive Implementation Guide

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [RAG Architecture](#rag-architecture)
4. [Prompt Engineering](#prompt-engineering)
5. [Agent Implementation](#agent-implementation)
6. [Memory Management](#memory-management)
7. [Production Best Practices](#production-best-practices)
8. [Complete Examples](#complete-examples)

---

## Overview

This guide covers building production-ready LLM agents using LangChain and LangGraph with:
- **Retrieval-Augmented Generation (RAG)** for grounding responses in external knowledge
- **Prompt Engineering** for optimal model behavior
- **Stateful Workflows** for complex multi-step tasks
- **Memory Systems** for context retention

### When to Use What

- **LangChain**: Use for building individual components (retrievers, tools, prompts)
- **LangGraph**: Use for orchestrating complex, stateful agent workflows with branching logic

---

## Core Concepts

### 1. Retrieval-Augmented Generation (RAG)

RAG enhances LLM responses by retrieving relevant context from external knowledge sources.

**Key Components:**
- **Document Loaders**: Ingest data from various sources
- **Text Splitters**: Break documents into manageable chunks
- **Embeddings**: Convert text to vector representations
- **Vector Stores**: Enable semantic search
- **Retrievers**: Query the vector store

### 2. Agents

Agents are LLM-powered systems that can:
- Reason about tasks
- Use tools to gather information
- Take actions based on observations
- Maintain state across interactions

### 3. State Management

**Short-term Memory**: In-context learning (conversation history)
**Long-term Memory**: Persistent storage across sessions
**Working Memory**: Intermediate state during execution

---

## RAG Architecture

### Basic RAG Pipeline

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

# 1. Load Documents
loader = WebBaseLoader(
    web_paths=("https://example.com/docs",),
    bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=("content")))
)
docs = loader.load()

# 2. Split Documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)
doc_splits = text_splitter.split_documents(docs)

# 3. Create Vector Store
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = InMemoryVectorStore.from_documents(
    documents=doc_splits,
    embedding=embeddings
)

# 4. Create Retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}
)
```

### Supported Embedding Providers

```python
# OpenAI
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Azure OpenAI
from langchain_openai import AzureOpenAIEmbeddings
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
)

# Cohere
from langchain_cohere import CohereEmbeddings
embeddings = CohereEmbeddings(model="embed-english-v3.0")

# Google Gemini
from langchain_google_genai import GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# NVIDIA
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
embeddings = NVIDIAEmbeddings(model="NV-Embed-QA")
```

### Vector Store Options

```python
# In-Memory (Development)
from langchain_core.vectorstores import InMemoryVectorStore
vectorstore = InMemoryVectorStore.from_documents(docs, embeddings)

# Qdrant (Production)
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(":memory:")
vectorstore = QdrantVectorStore(
    client=client,
    collection_name="knowledge_base",
    embedding=embeddings
)

# PostgreSQL with pgvector (Production)
from langchain_postgres import PGEngine, PGVectorStore

pg_engine = PGEngine.from_connection_string("postgresql+psycopg://...")
vectorstore = PGVectorStore.create_sync(
    engine=pg_engine,
    table_name='embeddings',
    embedding_service=embeddings
)
```

---

## Prompt Engineering

### 1. Static System Prompts

Best for consistent behavior across all interactions.

```python
from langchain.agents import create_agent

system_prompt = """
You are a helpful AI assistant specializing in software engineering.

Guidelines:
- Provide accurate, well-reasoned responses
- Cite sources when using retrieved information
- Admit uncertainty when appropriate
- Use clear, concise language
"""

agent = create_agent(
    model="openai:gpt-4o",
    tools=[],
    system_prompt=system_prompt
)
```

### 2. Dynamic Prompts with Context

Adapt prompts based on runtime context.

```python
from typing import TypedDict
from langchain.agents.middleware import dynamic_prompt, ModelRequest

class Context(TypedDict):
    user_role: str

@dynamic_prompt
def role_based_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on user role."""
    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "You are a helpful assistant."

    if user_role == "expert":
        return f"{base_prompt} Provide detailed technical responses."
    elif user_role == "beginner":
        return f"{base_prompt} Explain concepts simply and avoid jargon."

    return base_prompt

agent = create_agent(
    model="openai:gpt-4o",
    tools=[web_search],
    middleware=[role_based_prompt],
    context_schema=Context
)

# Invoke with context
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Explain machine learning"}]},
    context={"user_role": "expert"}
)
```

### 3. Context Injection with Retrieved Documents

```python
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    """Inject retrieved context into system message."""
    last_query = request.state["messages"][-1].text
    retrieved_docs = vector_store.similarity_search(last_query, k=2)

    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    system_message = (
        "You are a helpful assistant. Use the following context in your response:"
        f"\n\n{docs_content}"
    )

    return system_message

agent = create_agent(model, tools=[], middleware=[prompt_with_context])
```

### 4. Prompts with User Preferences from Store

```python
from dataclasses import dataclass
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

@dynamic_prompt
def store_aware_prompt(request: ModelRequest) -> str:
    user_id = request.runtime.context.user_id

    # Read from Store
    store = request.runtime.store
    user_prefs = store.get(("preferences",), user_id)

    base = "You are a helpful assistant."

    if user_prefs:
        style = user_prefs.value.get("communication_style", "balanced")
        base += f"\nUser prefers {style} responses."

    return base

agent = create_agent(
    model="openai:gpt-4o",
    tools=[...],
    middleware=[store_aware_prompt],
    context_schema=Context,
    store=InMemoryStore()
)
```

---

## Agent Implementation

### 1. Simple RAG Agent with LangChain

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

tools = [retrieve_context]

system_prompt = """
You have access to a tool that retrieves context from a knowledge base.
Use the tool to help answer user queries.
Always cite sources when using retrieved information.
"""

agent = create_agent(
    model="openai:gpt-4o",
    tools=tools,
    system_prompt=system_prompt
)

# Execute
response = agent.invoke({
    "messages": [{"role": "user", "content": "What is task decomposition?"}]
})
```

### 2. Agentic RAG with URL Fetching

```python
import requests
from langchain.tools import tool
from langchain.agents import create_agent

ALLOWED_DOMAINS = ["https://docs.example.com/"]

@tool
def fetch_documentation(url: str) -> str:
    """Fetch and convert documentation from a URL"""
    if not any(url.startswith(domain) for domain in ALLOWED_DOMAINS):
        return f"Error: URL not allowed. Must start with: {', '.join(ALLOWED_DOMAINS)}"

    response = requests.get(url, timeout=10.0)
    response.raise_for_status()
    return response.text

system_prompt = """
You are an expert technical assistant.

Instructions:
1. If unsure about API usage or configuration, use the fetch_documentation tool
2. When citing documentation, summarize clearly and include relevant context
3. Do not use any URLs outside of the allowed domains
4. If a fetch fails, proceed with your best expert understanding
"""

agent = create_agent(
    model="anthropic:claude-sonnet-4-0",
    tools=[fetch_documentation],
    system_prompt=system_prompt
)
```

### 3. Advanced LangGraph Agent with State Management

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

# Define state schema
class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: str
    context: list[str]

# Create graph builder
graph_builder = StateGraph(State)

# Define node functions
def fetch_user_info(state: State):
    """Fetch user data from database"""
    return {"user_info": "User details from database"}

def retrieve_context(state: State):
    """Retrieve relevant documents"""
    last_query = state["messages"][-1].content
    docs = vector_store.similarity_search(last_query, k=3)
    context = [doc.page_content for doc in docs]
    return {"context": context}

def chatbot(state: State):
    """Process with LLM"""
    context_str = "\n\n".join(state.get("context", []))

    system_msg = f"""
    You are a helpful assistant.

    User Info: {state.get('user_info', 'Unknown')}

    Context:
    {context_str}
    """

    messages = [{"role": "system", "content": system_msg}] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# Add nodes
graph_builder.add_node("fetch_user", fetch_user_info)
graph_builder.add_node("retrieve", retrieve_context)
graph_builder.add_node("chatbot", chatbot)

# Define routing logic
def should_retrieve(state: State) -> str:
    """Decide if we need to retrieve documents"""
    last_message = state["messages"][-1].content.lower()
    if any(keyword in last_message for keyword in ["find", "search", "what is"]):
        return "retrieve"
    return "chatbot"

# Add edges
graph_builder.add_edge(START, "fetch_user")
graph_builder.add_conditional_edges(
    "fetch_user",
    should_retrieve,
    {"retrieve": "retrieve", "chatbot": "chatbot"}
)
graph_builder.add_edge("retrieve", "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile with checkpointer
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Execute
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke(
    {"messages": [{"role": "user", "content": "What is machine learning?"}]},
    config=config
)
```

### 4. Multi-Step Agentic RAG with Document Grading

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools.retriever import create_retriever_tool

# Create retriever tool
retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_blog_posts",
    "Search and return information about blog posts."
)

class MessagesState(TypedDict):
    messages: Annotated[list, add_messages]

def generate_query_or_respond(state: MessagesState):
    """Agent decides whether to retrieve or respond"""
    messages = state["messages"]
    model_with_tools = model.bind_tools([retriever_tool])
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def grade_documents(state: MessagesState):
    """Assess document relevance"""
    last_message = state["messages"][-1]

    # Check if documents were retrieved
    if not hasattr(last_message, "tool_calls"):
        return "generate_answer"

    # Grade documents (simplified)
    # In production, use an LLM to grade relevance
    return "generate_answer"  # or "rewrite_question"

def rewrite_question(state: MessagesState):
    """Transform query for better retrieval"""
    messages = state["messages"]
    question = messages[0].content

    msg = [
        {"role": "system", "content": "Rewrite the question to improve retrieval."},
        {"role": "user", "content": question}
    ]

    response = model.invoke(msg)
    return {"messages": [response]}

def generate_answer(state: MessagesState):
    """Generate final answer"""
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# Build workflow
workflow = StateGraph(MessagesState)

workflow.add_node("generate_query_or_respond", generate_query_or_respond)
workflow.add_node("retrieve", ToolNode([retriever_tool]))
workflow.add_node("rewrite_question", rewrite_question)
workflow.add_node("generate_answer", generate_answer)

# Add edges
workflow.add_edge(START, "generate_query_or_respond")
workflow.add_conditional_edges(
    "generate_query_or_respond",
    tools_condition,
    {"tools": "retrieve", END: END}
)
workflow.add_conditional_edges("retrieve", grade_documents)
workflow.add_edge("generate_answer", END)
workflow.add_edge("rewrite_question", "generate_query_or_respond")

# Compile
graph = workflow.compile()
```

---

## Memory Management

### 1. Short-Term Memory (Conversation History)

LangGraph automatically manages conversation history with checkpointers.

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[get_weather],
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "1"}}

# First message
agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    config
)

# Continues conversation
agent.invoke(
    {"messages": [{"role": "user", "content": "what about new york?"}]},
    config
)
```

### 2. PostgreSQL for Production Persistence

```python
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://postgres:postgres@localhost:5432/agents"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()  # Create tables

    def call_model(state: MessagesState):
        response = model.invoke(state["messages"])
        return {"messages": response}

    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_edge(START, "call_model")

    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "user-001"}}

    graph.invoke(
        {"messages": [{"role": "user", "content": "hi! I'm bob"}]},
        config
    )

    # Later session - remembers "bob"
    graph.invoke(
        {"messages": [{"role": "user", "content": "what's my name?"}]},
        config
    )
```

### 3. Long-Term Memory with Semantic Search

```python
from langchain.embeddings import init_embeddings
from langgraph.store.memory import InMemoryStore

# Create store with semantic search
embeddings = init_embeddings("openai:text-embedding-3-small")
store = InMemoryStore(
    index={
        "embed": embeddings,
        "dims": 1536,
    }
)

# Populate with user memories
store.put(("user_123", "memories"), "1", {"text": "I love pizza"})
store.put(("user_123", "memories"), "2", {"text": "I am a plumber"})
store.put(("user_123", "memories"), "3", {"text": "My favorite color is blue"})

def chat(state: MessagesState, *, store):
    """Chat node with memory retrieval"""
    # Search based on user's last message
    items = store.search(
        ("user_123", "memories"),
        query=state["messages"][-1].content,
        limit=2
    )

    memories = "\n".join(item.value["text"] for item in items)
    memories = f"## User Memories\n{memories}" if memories else ""

    response = llm.invoke([
        {"role": "system", "content": f"You are a helpful assistant.\n{memories}"},
        *state["messages"],
    ])

    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node(chat)
builder.add_edge(START, "chat")
graph = builder.compile(store=store)

# Agent will use relevant memories
result = graph.invoke({
    "messages": [{"role": "user", "content": "I'm hungry"}]
})
# Response will reference "I love pizza"
```

### 4. Tool Access to Long-Term Memory

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

store = InMemoryStore()

# Write user data
store.put(
    ("users",),
    "user_123",
    {"name": "John Smith", "language": "English"}
)

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """Look up user info."""
    store = runtime.store
    user_id = runtime.context.user_id

    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[get_user_info],
    store=store,
    context_schema=Context
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "look up user information"}]},
    context=Context(user_id="user_123")
)
```

### 5. Updating State from Tools

```python
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.types import Command

class CustomState(AgentState):
    user_name: str

def update_user_info(
    tool_call_id: Annotated[str, InjectedToolCallId],
    config: RunnableConfig
) -> Command:
    """Look up and update user info."""
    user_id = config["configurable"].get("user_id")
    name = "John Smith" if user_id == "user_123" else "Unknown user"

    return Command(update={
        "user_name": name,
        "messages": [
            ToolMessage("Successfully looked up user information", tool_call_id=tool_call_id)
        ]
    })

def greet(state: Annotated[CustomState, InjectedState]) -> str:
    """Use this to greet the user once you found their info."""
    user_name = state["user_name"]
    return f"Hello {user_name}!"

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[update_user_info, greet],
    state_schema=CustomState
)
```

---

## Production Best Practices

### 1. Observability with LangSmith

```python
import os
import getpass

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
```

### 2. Error Handling

```python
from pydantic import BaseModel, Field
from langchain.agents.structured_output import ToolStrategy

class ProductRating(BaseModel):
    rating: int | None = Field(description="Rating from 1-5", ge=1, le=5)
    comment: str = Field(description="Review comment")

agent = create_agent(
    model="openai:gpt-4o",
    tools=[],
    response_format=ToolStrategy(ProductRating),  # Handles validation errors
    system_prompt="Parse product reviews accurately. Do not fabricate data."
)
```

### 3. Task Management with Middleware

```python
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model="openai:gpt-4o",
    tools=[...],
    middleware=[TodoListMiddleware()]
)

result = agent.invoke({"messages": [{"role": "user", "content": "Refactor my codebase"}]})
print(result["todos"])  # Track progress
```

### 4. Dynamic Tool Selection

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest

class ToolSelectorMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
    ) -> ModelResponse:
        """Select relevant tools based on state/context."""
        relevant_tools = select_relevant_tools(request.state, request.runtime)
        request.tools = relevant_tools
        return handler(request)

agent = create_agent(
    model="openai:gpt-4o",
    tools=all_tools,
    middleware=[ToolSelectorMiddleware()]
)
```

### 5. Streaming Responses

```python
# Stream values
for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "What is task decomposition?"}]},
    config,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

# Stream messages only
for message, metadata in graph.stream(
    {"messages": [{"role": "user", "content": "I'm hungry"}]},
    stream_mode="messages"
):
    print(message.content, end="")
```

### 6. State History and Debugging

```python
# Get state history
config = {"configurable": {"thread_id": "1"}}

history = []
for state in graph.get_state_history(config):
    history.append(state)

# Inspect state
current_state = graph.get_state(config)
print(current_state.values)
```

---

## Complete Examples

### Example 1: Customer Support Agent with RAG

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver

# 1. Load and index documentation
loader = WebBaseLoader(web_paths=("https://docs.company.com/",))
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
doc_splits = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = InMemoryVectorStore.from_documents(doc_splits, embeddings)

# 2. Create retrieval tool
@tool(response_format="content_and_artifact")
def search_documentation(query: str):
    """Search company documentation for relevant information."""
    docs = vectorstore.similarity_search(query, k=3)
    serialized = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
        for doc in docs
    )
    return serialized, docs

# 3. Create support tools
@tool
def create_ticket(issue: str, priority: str) -> str:
    """Create a support ticket for the customer."""
    # In production, integrate with ticketing system
    ticket_id = f"TICKET-{hash(issue) % 10000}"
    return f"Created ticket {ticket_id} with priority {priority}"

# 4. Define agent
system_prompt = """
You are a helpful customer support agent.

Guidelines:
- Always search documentation first to provide accurate answers
- Be empathetic and professional
- If you can't resolve an issue, create a support ticket
- Cite documentation sources when applicable
"""

DB_URI = "postgresql://postgres:postgres@localhost:5432/support"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()

    agent = create_agent(
        model="openai:gpt-4o",
        tools=[search_documentation, create_ticket],
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )

    # 5. Handle customer conversation
    config = {"configurable": {"thread_id": "customer-456"}}

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "How do I reset my password?"}]},
        config
    )

    print(response["messages"][-1].content)
```

### Example 2: Research Assistant with Multi-Step RAG

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    documents: list
    search_queries: list[str]
    final_report: str

def generate_search_queries(state: ResearchState):
    """Generate multiple search queries for comprehensive research"""
    question = state["messages"][-1].content

    prompt = f"""
    Generate 3 diverse search queries to research this question comprehensively:
    {question}

    Return as JSON array: ["query1", "query2", "query3"]
    """

    response = llm.invoke([{"role": "user", "content": prompt}])
    queries = json.loads(response.content)

    return {"question": question, "search_queries": queries}

def retrieve_documents(state: ResearchState):
    """Retrieve documents for all queries"""
    all_docs = []

    for query in state["search_queries"]:
        docs = vectorstore.similarity_search(query, k=2)
        all_docs.extend(docs)

    # Deduplicate
    unique_docs = {doc.page_content: doc for doc in all_docs}.values()

    return {"documents": list(unique_docs)}

def grade_documents(state: ResearchState):
    """Filter out irrelevant documents"""
    question = state["question"]
    relevant_docs = []

    for doc in state["documents"]:
        prompt = f"""
        Question: {question}
        Document: {doc.page_content}

        Is this document relevant? Answer 'yes' or 'no'.
        """

        response = llm.invoke([{"role": "user", "content": prompt}])

        if "yes" in response.content.lower():
            relevant_docs.append(doc)

    return {"documents": relevant_docs}

def should_continue(state: ResearchState) -> Literal["generate", "rewrite"]:
    """Decide whether to generate report or rewrite question"""
    if len(state["documents"]) >= 3:
        return "generate"
    return "rewrite"

def rewrite_question(state: ResearchState):
    """Rewrite question for better retrieval"""
    prompt = f"""
    The following question didn't retrieve enough relevant documents:
    {state["question"]}

    Rewrite it to be more specific and searchable.
    """

    response = llm.invoke([{"role": "user", "content": prompt}])

    return {
        "messages": [{"role": "assistant", "content": f"Rewriting query: {response.content}"}],
        "question": response.content
    }

def generate_report(state: ResearchState):
    """Generate final research report"""
    docs_content = "\n\n".join(
        f"Source {i+1}: {doc.page_content}"
        for i, doc in enumerate(state["documents"])
    )

    prompt = f"""
    Question: {state["question"]}

    Research Materials:
    {docs_content}

    Write a comprehensive research report answering the question.
    Include citations to sources.
    """

    response = llm.invoke([{"role": "user", "content": prompt}])

    return {
        "messages": [{"role": "assistant", "content": response.content}],
        "final_report": response.content
    }

# Build workflow
workflow = StateGraph(ResearchState)

workflow.add_node("generate_queries", generate_search_queries)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("grade", grade_documents)
workflow.add_node("rewrite", rewrite_question)
workflow.add_node("generate", generate_report)

workflow.add_edge(START, "generate_queries")
workflow.add_edge("generate_queries", "retrieve")
workflow.add_edge("retrieve", "grade")
workflow.add_conditional_edges("grade", should_continue)
workflow.add_edge("rewrite", "generate_queries")
workflow.add_edge("generate", END)

memory = InMemorySaver()
research_agent = workflow.compile(checkpointer=memory)

# Execute
config = {"configurable": {"thread_id": "research-001"}}
result = research_agent.invoke(
    {"messages": [{"role": "user", "content": "What are the latest developments in quantum computing?"}]},
    config
)

print(result["final_report"])
```

---

## Key Takeaways

1. **RAG is Essential**: Ground LLM responses in factual data using retrieval
2. **Prompt Engineering Matters**: Use static prompts for consistency, dynamic prompts for personalization
3. **Choose the Right Tool**: LangChain for components, LangGraph for complex workflows
4. **Memory is Critical**: Use checkpointers for conversations, stores for long-term knowledge
5. **Production-Ready**: Implement observability, error handling, and proper persistence
6. **Start Simple**: Begin with basic RAG, add complexity as needed
7. **Test Thoroughly**: Use LangSmith for debugging and monitoring
8. **Optimize Retrieval**: Tune chunk size, overlap, and retrieval parameters
9. **Handle Errors**: Implement graceful degradation and retry logic
10. **Monitor Performance**: Track token usage, latency, and accuracy

---

## Resources

- **LangChain Documentation**: https://docs.langchain.com/
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **LangSmith**: https://smith.langchain.com/
- **Vector Store Options**: Qdrant, Pinecone, Weaviate, PostgreSQL pgvector
- **Embedding Models**: OpenAI, Cohere, Google, NVIDIA, Voyage AI

---

## Next Steps

1. Set up your development environment
2. Implement a basic RAG pipeline
3. Add agent capabilities with tools
4. Integrate memory and state management
5. Build complex workflows with LangGraph
6. Deploy to production with proper monitoring
7. Iterate based on user feedback and metrics
