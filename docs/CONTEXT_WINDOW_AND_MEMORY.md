# Context Window Management & Conversational Memory

**A comprehensive guide to managing context and memory in AI agent systems**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Context Window Fundamentals](#context-window-fundamentals)
3. [Context Window Management Strategies](#context-window-management-strategies)
4. [Conversational Memory Systems](#conversational-memory-systems)
5. [Implementation Patterns](#implementation-patterns)
6. [Best Practices](#best-practices)
7. [Poker Advisor Application](#poker-advisor-application)
8. [Common Pitfalls](#common-pitfalls)

---

## Introduction

### The Problem

Modern LLMs have finite context windows (e.g., GPT-4: 128k tokens, Claude: 200k tokens). In conversational AI systems, this creates two critical challenges:

1. **Context Overflow**: Long conversations exceed the model's capacity
2. **Memory Loss**: Stateless systems forget previous interactions

### The Solution

A combination of:
- **Context Window Management**: Intelligent selection and compression of information
- **Conversational Memory**: Persistent storage and retrieval of conversation history

---

## Context Window Fundamentals

### What Is a Context Window?

The context window is the **maximum amount of text** an LLM can process in a single request, measured in tokens.

**Token counts** (approximate):
- 1 token ≈ 4 characters of English text
- 1 token ≈ 0.75 words
- Example: "Hello, how are you?" = ~5 tokens

### Context Window Anatomy

A typical LLM request contains:

```
┌─────────────────────────────────────────┐
│ System Prompt          (500-2000 tokens)│
├─────────────────────────────────────────┤
│ Retrieved Context      (1000-5000 tokens│ ← RAG results
├─────────────────────────────────────────┤
│ Conversation History   (0-50000 tokens) │ ← Previous messages
├─────────────────────────────────────────┤
│ Current User Query     (10-500 tokens)  │
├─────────────────────────────────────────┤
│ Tool Call Results      (0-10000 tokens) │ ← Function outputs
└─────────────────────────────────────────┘
Total: 1,510 - 67,500 tokens
```

### Why Context Management Matters

**Without management**:
- ❌ Context overflow → truncation → lost information
- ❌ Irrelevant information → diluted attention → worse responses
- ❌ High token costs → expensive API calls

**With management**:
- ✅ Optimal information density
- ✅ Consistent performance across long conversations
- ✅ Cost efficiency

---

## Context Window Management Strategies

### 1. Sliding Window

**Concept**: Keep only the N most recent messages.

```python
class SlidingWindowMemory:
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.messages = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Keep only last N messages
        if len(self.messages) > self.window_size:
            self.messages = self.messages[-self.window_size:]

    def get_context(self) -> List[Dict]:
        return self.messages
```

**Pros**:
- ✅ Simple to implement
- ✅ Bounded memory usage
- ✅ Prevents context overflow

**Cons**:
- ❌ Loses important earlier context
- ❌ No semantic understanding of importance

**Use cases**:
- Short-term conversations
- Chat interfaces with no long-term memory needs

---

### 2. Summarization

**Concept**: Periodically compress old messages into summaries.

```python
class SummarizingMemory:
    def __init__(self, llm, summary_threshold: int = 20):
        self.llm = llm
        self.summary_threshold = summary_threshold
        self.messages = []
        self.summary = ""

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

        # Summarize if we exceed threshold
        if len(self.messages) > self.summary_threshold:
            self._summarize_and_compress()

    def _summarize_and_compress(self):
        # Ask LLM to summarize old messages
        old_messages = self.messages[:-5]  # Keep last 5
        summary_prompt = f"""
        Summarize this conversation concisely, preserving key facts and decisions:

        {old_messages}

        Previous summary: {self.summary}
        """

        new_summary = self.llm.generate(summary_prompt)

        # Update state
        self.summary = new_summary
        self.messages = self.messages[-5:]  # Keep recent messages

    def get_context(self) -> str:
        context = f"Conversation summary: {self.summary}\n\n"
        context += "Recent messages:\n"
        for msg in self.messages:
            context += f"{msg['role']}: {msg['content']}\n"
        return context
```

**Pros**:
- ✅ Preserves important information from entire history
- ✅ Bounded context size
- ✅ Semantic understanding of what matters

**Cons**:
- ❌ Summarization can lose details
- ❌ Additional LLM calls (cost + latency)
- ❌ Potential information degradation over multiple summaries

**Use cases**:
- Long-form tutoring sessions
- Customer support with extended history
- Complex multi-turn problem solving

---

### 3. Hierarchical Retrieval

**Concept**: Store conversation at multiple granularities and retrieve hierarchically.

```python
class HierarchicalMemory:
    """
    Three-tier memory system:
    1. Session summary (high-level)
    2. Topic summaries (medium-level)
    3. Full messages (detailed)
    """

    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.session_summary = ""
        self.topic_summaries = {}
        self.current_topic = None
        self.messages = []

    def add_message(self, role: str, content: str):
        # Store full message
        self.messages.append({
            "role": role,
            "content": content,
            "topic": self.current_topic,
            "embedding": self.vector_store.embed(content)
        })

        # Update topic summary if topic changed
        if self._topic_changed(content):
            self._summarize_topic()
            self.current_topic = self._detect_topic(content)

    def retrieve_context(self, query: str, max_tokens: int) -> str:
        """Hierarchical retrieval based on query"""

        # 1. Always include session summary (high-level context)
        context = f"Session Summary: {self.session_summary}\n\n"
        remaining_tokens = max_tokens - self._count_tokens(context)

        # 2. Retrieve relevant topic summaries
        relevant_topics = self._find_relevant_topics(query, k=3)
        for topic in relevant_topics:
            topic_context = f"Topic: {topic}\nSummary: {self.topic_summaries[topic]}\n\n"
            if self._count_tokens(topic_context) < remaining_tokens:
                context += topic_context
                remaining_tokens -= self._count_tokens(topic_context)

        # 3. Fill remaining space with most relevant full messages
        relevant_messages = self._semantic_search(query, k=10)
        for msg in relevant_messages:
            msg_text = f"{msg['role']}: {msg['content']}\n"
            if self._count_tokens(msg_text) < remaining_tokens:
                context += msg_text
                remaining_tokens -= self._count_tokens(msg_text)
            else:
                break

        return context

    def _semantic_search(self, query: str, k: int) -> List[Dict]:
        """Vector similarity search over messages"""
        query_embedding = self.vector_store.embed(query)

        # Find k most similar messages
        similarities = []
        for msg in self.messages:
            similarity = self._cosine_similarity(query_embedding, msg['embedding'])
            similarities.append((similarity, msg))

        # Sort by similarity and return top k
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [msg for _, msg in similarities[:k]]
```

**Pros**:
- ✅ Flexible retrieval based on query
- ✅ Preserves both high-level and detailed context
- ✅ Efficient use of context window
- ✅ Semantic relevance

**Cons**:
- ❌ Complex to implement
- ❌ Requires vector embeddings
- ❌ Higher computational cost

**Use cases**:
- Multi-session applications
- Complex domain knowledge (poker strategy)
- Educational systems with progressive learning

---

### 4. Importance-Based Filtering

**Concept**: Assign importance scores to messages and keep the most important ones.

```python
class ImportanceBasedMemory:
    def __init__(self, llm, max_messages: int = 15):
        self.llm = llm
        self.max_messages = max_messages
        self.messages = []

    def add_message(self, role: str, content: str):
        # Calculate importance score
        importance = self._calculate_importance(content)

        self.messages.append({
            "role": role,
            "content": content,
            "importance": importance,
            "timestamp": datetime.now()
        })

        # Prune if necessary
        if len(self.messages) > self.max_messages:
            self._prune_low_importance()

    def _calculate_importance(self, content: str) -> float:
        """
        Score importance based on:
        - Contains decisions/commitments
        - Contains key facts
        - User questions (high importance)
        - System confirmations (low importance)
        """

        importance = 0.5  # baseline

        # Heuristic: questions are important
        if "?" in content:
            importance += 0.3

        # Keywords indicating decisions
        decision_keywords = ["decide", "commit", "agree", "will", "must"]
        if any(kw in content.lower() for kw in decision_keywords):
            importance += 0.3

        # Facts/definitions are important
        fact_keywords = ["is defined as", "means", "equals", "represents"]
        if any(kw in content.lower() for kw in fact_keywords):
            importance += 0.2

        # Short confirmations are less important
        if len(content.split()) < 5:
            importance -= 0.2

        return min(1.0, max(0.0, importance))

    def _prune_low_importance(self):
        """Keep only most important messages"""
        # Always keep the most recent message
        recent = self.messages[-1]

        # Sort rest by importance
        rest = sorted(self.messages[:-1],
                     key=lambda x: x['importance'],
                     reverse=True)

        # Keep top N-1 most important + most recent
        self.messages = rest[:self.max_messages-1] + [recent]

        # Re-sort by timestamp for chronological order
        self.messages.sort(key=lambda x: x['timestamp'])
```

**Pros**:
- ✅ Preserves most critical information
- ✅ Adaptive to conversation content
- ✅ Better than simple sliding window

**Cons**:
- ❌ Importance scoring is heuristic (can be wrong)
- ❌ May lose important context if scoring fails
- ❌ Requires tuning for specific domains

**Use cases**:
- Business conversations (preserve decisions)
- Technical support (keep problem statements and solutions)
- Any domain with clear "important" vs "filler" messages

---

### 5. Token Budget Management

**Concept**: Allocate fixed token budgets to different context components.

```python
class TokenBudgetManager:
    def __init__(self,
                 total_budget: int = 8000,
                 system_prompt_budget: int = 1000,
                 rag_budget: int = 3000,
                 history_budget: int = 3000,
                 user_query_budget: int = 500,
                 tool_results_budget: int = 500):

        self.budgets = {
            'system_prompt': system_prompt_budget,
            'rag': rag_budget,
            'history': history_budget,
            'user_query': user_query_budget,
            'tool_results': tool_results_budget
        }

        # Verify budgets sum to total
        assert sum(self.budgets.values()) == total_budget

    def build_context(self,
                     system_prompt: str,
                     rag_results: List[str],
                     conversation_history: List[Dict],
                     user_query: str,
                     tool_results: List[str]) -> str:
        """
        Build context while respecting token budgets
        """

        context_parts = {}

        # 1. System prompt (fixed, truncate if necessary)
        context_parts['system_prompt'] = self._truncate(
            system_prompt,
            self.budgets['system_prompt']
        )

        # 2. RAG results (prioritize by relevance)
        context_parts['rag'] = self._fit_rag_results(
            rag_results,
            self.budgets['rag']
        )

        # 3. Conversation history (most recent first)
        context_parts['history'] = self._fit_history(
            conversation_history,
            self.budgets['history']
        )

        # 4. User query (must fit entirely)
        context_parts['user_query'] = self._truncate(
            user_query,
            self.budgets['user_query']
        )

        # 5. Tool results (most recent)
        context_parts['tool_results'] = self._fit_tool_results(
            tool_results,
            self.budgets['tool_results']
        )

        # Assemble final context
        return self._assemble_context(context_parts)

    def _fit_rag_results(self, results: List[str], budget: int) -> str:
        """Fit RAG results within budget, prioritizing earlier (more relevant) results"""
        context = ""
        for result in results:
            result_tokens = self._count_tokens(result)
            if result_tokens <= budget:
                context += result + "\n\n"
                budget -= result_tokens
            else:
                # Truncate last result to fit
                context += self._truncate(result, budget)
                break
        return context

    def _fit_history(self, history: List[Dict], budget: int) -> str:
        """Fit conversation history, keeping most recent messages"""
        context = ""
        # Reverse to prioritize recent
        for msg in reversed(history):
            msg_text = f"{msg['role']}: {msg['content']}\n"
            msg_tokens = self._count_tokens(msg_text)

            if msg_tokens <= budget:
                # Prepend (since we're going backwards)
                context = msg_text + context
                budget -= msg_tokens
            else:
                break
        return context

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # More accurate: use tiktoken library
        return len(text) // 4  # Rough estimate: 4 chars per token

    def _truncate(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit token budget"""
        estimated_chars = max_tokens * 4
        if len(text) <= estimated_chars:
            return text
        return text[:estimated_chars] + "... [truncated]"
```

**Pros**:
- ✅ Predictable context composition
- ✅ Prevents any single component from dominating
- ✅ Easy to tune for specific use cases
- ✅ Guaranteed to fit in context window

**Cons**:
- ❌ Fixed budgets may not be optimal for all queries
- ❌ Requires careful budget tuning
- ❌ May waste budget if components are smaller than allocated

**Use cases**:
- Production systems requiring reliability
- Multi-component agents (RAG + tools + history)
- Cost-sensitive applications

---

## Conversational Memory Systems

### Short-Term vs Long-Term Memory

```
┌─────────────────────────────────────────────────────────┐
│                    MEMORY HIERARCHY                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │ Short-Term Memory (Current Session)           │    │
│  │ - Active conversation                         │    │
│  │ - Immediate context                           │    │
│  │ - Volatility: Cleared on session end          │    │
│  │ - Storage: In-memory                          │    │
│  │ - Retrieval: Direct access                    │    │
│  └───────────────────────────────────────────────┘    │
│                        ↓ Summarization                 │
│  ┌───────────────────────────────────────────────┐    │
│  │ Working Memory (Recent Sessions)              │    │
│  │ - Last N sessions                             │    │
│  │ - Key facts and preferences                   │    │
│  │ - Volatility: Expires after N days            │    │
│  │ - Storage: Database/Redis                     │    │
│  │ - Retrieval: Semantic search                  │    │
│  └───────────────────────────────────────────────┘    │
│                        ↓ Consolidation                 │
│  ┌───────────────────────────────────────────────┐    │
│  │ Long-Term Memory (User Profile)               │    │
│  │ - Persistent facts                            │    │
│  │ - Learning progress                           │    │
│  │ - Preferences and patterns                    │    │
│  │ - Volatility: Permanent                       │    │
│  │ - Storage: Database + Vector DB               │    │
│  │ - Retrieval: Hybrid (SQL + semantic)          │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### 1. Session Memory

**Concept**: Remember the current conversation only.

```python
class SessionMemory:
    """In-memory storage for current conversation"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.started_at = datetime.now()
        self.messages: List[Dict] = []
        self.metadata: Dict = {
            'user_id': None,
            'topic': None,
            'goals': []
        }

    def add_message(self, role: str, content: str, metadata: Dict = None):
        msg = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        self.messages.append(msg)

    def get_recent_messages(self, n: int = 10) -> List[Dict]:
        """Get last N messages"""
        return self.messages[-n:]

    def get_full_history(self) -> List[Dict]:
        """Get all messages in session"""
        return self.messages

    def set_metadata(self, key: str, value: Any):
        """Store session-level metadata"""
        self.metadata[key] = value

    def get_session_summary(self) -> str:
        """Generate summary of session"""
        return f"""
        Session ID: {self.session_id}
        Duration: {datetime.now() - self.started_at}
        Messages: {len(self.messages)}
        Topic: {self.metadata.get('topic', 'Unknown')}
        """
```

---

### 2. User Profile Memory

**Concept**: Persistent storage of user-specific information.

```python
class UserProfile:
    """Long-term user profile with learning progress"""

    def __init__(self, user_id: str, db_connection):
        self.user_id = user_id
        self.db = db_connection
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict:
        """Load from database"""
        result = self.db.query(
            "SELECT * FROM user_profiles WHERE user_id = ?",
            (self.user_id,)
        )

        if result:
            return result[0]
        else:
            # Create new profile
            return self._create_profile()

    def _create_profile(self) -> Dict:
        profile = {
            'user_id': self.user_id,
            'created_at': datetime.now(),
            'skill_level': 'beginner',
            'completed_lessons': [],
            'preferences': {},
            'statistics': {
                'total_sessions': 0,
                'total_questions': 0,
                'concepts_mastered': []
            }
        }

        self.db.execute(
            "INSERT INTO user_profiles VALUES (?, ?, ?, ?, ?, ?)",
            (profile['user_id'], profile['created_at'],
             profile['skill_level'], json.dumps(profile['completed_lessons']),
             json.dumps(profile['preferences']), json.dumps(profile['statistics']))
        )

        return profile

    def update_learning_progress(self, concept: str, mastery_level: float):
        """Track what user has learned"""
        if concept not in self.profile['completed_lessons']:
            self.profile['completed_lessons'].append({
                'concept': concept,
                'mastery_level': mastery_level,
                'learned_at': datetime.now()
            })
            self._save_profile()

    def get_skill_level(self) -> str:
        """Determine user's current skill level"""
        mastered = len(self.profile['statistics']['concepts_mastered'])

        if mastered < 5:
            return 'beginner'
        elif mastered < 15:
            return 'intermediate'
        else:
            return 'advanced'

    def set_preference(self, key: str, value: Any):
        """Store user preference"""
        self.profile['preferences'][key] = value
        self._save_profile()

    def _save_profile(self):
        """Persist to database"""
        self.db.execute(
            "UPDATE user_profiles SET completed_lessons = ?, preferences = ?, statistics = ? WHERE user_id = ?",
            (json.dumps(self.profile['completed_lessons']),
             json.dumps(self.profile['preferences']),
             json.dumps(self.profile['statistics']),
             self.user_id)
        )
```

---

### 3. Episodic Memory (RAG for Conversations)

**Concept**: Store and retrieve past conversations semantically.

```python
class EpisodicMemory:
    """
    Vector-based storage of conversation episodes
    Enables semantic retrieval of past interactions
    """

    def __init__(self, vector_store, embeddings_model):
        self.vector_store = vector_store
        self.embeddings = embeddings_model

    def store_episode(self,
                     session_id: str,
                     user_id: str,
                     messages: List[Dict],
                     summary: str,
                     metadata: Dict):
        """
        Store a completed conversation session
        """

        # Create episode document
        episode = {
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.now(),
            'summary': summary,
            'message_count': len(messages),
            'metadata': metadata,
            'full_transcript': json.dumps(messages)
        }

        # Generate embedding from summary
        embedding = self.embeddings.embed(summary)

        # Store in vector database
        self.vector_store.upsert(
            id=session_id,
            values=embedding,
            metadata=episode
        )

    def recall_similar_episodes(self,
                                query: str,
                                user_id: str,
                                k: int = 3) -> List[Dict]:
        """
        Find past conversations similar to current query

        Example:
        Query: "How do I calculate pot odds?"
        Returns: [
            {session from 2 weeks ago where user learned pot odds},
            {session from 1 month ago where user struggled with odds},
            ...
        ]
        """

        # Generate query embedding
        query_embedding = self.embeddings.embed(query)

        # Search vector store
        results = self.vector_store.query(
            vector=query_embedding,
            filter={'user_id': user_id},
            top_k=k
        )

        # Reconstruct episodes
        episodes = []
        for result in results:
            episode = result['metadata']
            episode['similarity_score'] = result['score']
            episode['messages'] = json.loads(episode['full_transcript'])
            episodes.append(episode)

        return episodes

    def get_learning_history(self, user_id: str, concept: str) -> List[Dict]:
        """
        Retrieve all past interactions about a specific concept

        Use case: "You asked about pot odds 3 times before.
                   Let me review what we covered..."
        """

        query = f"learning about {concept}"
        return self.recall_similar_episodes(query, user_id, k=10)
```

---

### 4. Hybrid Memory System

**Complete system combining all memory types**:

```python
class HybridMemorySystem:
    """
    Production-ready memory system combining:
    - Session memory (short-term)
    - User profile (long-term facts)
    - Episodic memory (past conversations)
    - Context management (dynamic retrieval)
    """

    def __init__(self, user_id: str, session_id: str, config: Dict):
        # Short-term: Current session
        self.session = SessionMemory(session_id)

        # Long-term: User profile
        self.profile = UserProfile(user_id, config['db'])

        # Episodic: Past conversations
        self.episodes = EpisodicMemory(
            config['vector_store'],
            config['embeddings']
        )

        # Context manager
        self.context_manager = TokenBudgetManager(
            total_budget=config.get('context_budget', 8000)
        )

    def add_interaction(self, user_msg: str, assistant_msg: str):
        """Record a user-assistant interaction"""
        self.session.add_message('user', user_msg)
        self.session.add_message('assistant', assistant_msg)

    def build_context_for_query(self, query: str, max_tokens: int = 8000) -> str:
        """
        Intelligently construct context from all memory sources

        Priority:
        1. Current session (most recent)
        2. User profile (preferences, skill level)
        3. Relevant past episodes (semantic match)
        4. System knowledge (RAG)
        """

        context_components = {
            'current_session': self._get_session_context(),
            'user_profile': self._get_profile_context(),
            'past_episodes': self._get_episodic_context(query),
        }

        # Use token budget manager to fit everything
        return self.context_manager.assemble_context(
            context_components,
            max_tokens=max_tokens
        )

    def _get_session_context(self) -> str:
        """Format current session for context"""
        recent = self.session.get_recent_messages(n=10)

        context = "=== CURRENT SESSION ===\n"
        for msg in recent:
            context += f"{msg['role']}: {msg['content']}\n"
        return context

    def _get_profile_context(self) -> str:
        """Format user profile for context"""
        p = self.profile.profile

        return f"""
        === USER PROFILE ===
        Skill Level: {self.profile.get_skill_level()}
        Completed Lessons: {len(p['completed_lessons'])}
        Last Mastered Concept: {p['statistics']['concepts_mastered'][-1] if p['statistics']['concepts_mastered'] else 'None'}
        Preferences: {p['preferences']}
        """

    def _get_episodic_context(self, query: str) -> str:
        """Retrieve relevant past conversations"""
        episodes = self.episodes.recall_similar_episodes(
            query,
            self.profile.user_id,
            k=2
        )

        if not episodes:
            return ""

        context = "=== RELEVANT PAST CONVERSATIONS ===\n"
        for ep in episodes:
            context += f"\n[{ep['timestamp']}] {ep['summary']}\n"
            context += f"Outcome: {ep['metadata'].get('outcome', 'Unknown')}\n"

        return context

    def end_session(self, llm):
        """Save session to long-term memory"""

        # Generate session summary
        summary = self._generate_summary(llm)

        # Extract key learnings
        concepts_learned = self._extract_concepts(llm)

        # Update user profile
        for concept in concepts_learned:
            self.profile.update_learning_progress(concept, mastery_level=0.7)

        # Store episode
        self.episodes.store_episode(
            session_id=self.session.session_id,
            user_id=self.profile.user_id,
            messages=self.session.get_full_history(),
            summary=summary,
            metadata={
                'concepts_learned': concepts_learned,
                'duration': str(datetime.now() - self.session.started_at)
            }
        )

    def _generate_summary(self, llm) -> str:
        """Ask LLM to summarize the session"""
        messages = self.session.get_full_history()

        prompt = f"""
        Summarize this conversation in 2-3 sentences, focusing on:
        - Main topic discussed
        - Key concepts learned
        - User's progress/understanding

        Conversation:
        {json.dumps(messages, indent=2)}
        """

        return llm.generate(prompt)

    def _extract_concepts(self, llm) -> List[str]:
        """Extract poker concepts that were taught"""
        messages = self.session.get_full_history()

        prompt = f"""
        Extract a list of poker concepts that were taught or discussed:

        Examples: ["pot odds", "equity calculation", "implied odds"]

        Conversation:
        {json.dumps(messages, indent=2)}

        Return ONLY a JSON array of concepts.
        """

        response = llm.generate(prompt)
        return json.loads(response)
```

---

## Implementation Patterns

### Pattern 1: Lazy Loading

**Don't load everything upfront - load as needed**

```python
class LazyMemoryLoader:
    """Load memory components only when accessed"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self._profile = None
        self._episodes = None

    @property
    def profile(self) -> UserProfile:
        """Load profile on first access"""
        if self._profile is None:
            self._profile = UserProfile.load(self.user_id)
        return self._profile

    @property
    def episodes(self) -> List[Dict]:
        """Load episodes on first access"""
        if self._episodes is None:
            self._episodes = EpisodicMemory.load_for_user(self.user_id)
        return self._episodes
```

---

### Pattern 2: Write-Through Cache

**Cache frequently accessed data in memory**

```python
class CachedMemory:
    """Cache user profile in Redis for fast access"""

    def __init__(self, redis_client, db_connection):
        self.redis = redis_client
        self.db = db_connection
        self.cache_ttl = 3600  # 1 hour

    def get_profile(self, user_id: str) -> Dict:
        # Try cache first
        cached = self.redis.get(f"profile:{user_id}")
        if cached:
            return json.loads(cached)

        # Load from DB
        profile = self.db.load_profile(user_id)

        # Write to cache
        self.redis.setex(
            f"profile:{user_id}",
            self.cache_ttl,
            json.dumps(profile)
        )

        return profile

    def update_profile(self, user_id: str, updates: Dict):
        # Update DB
        self.db.update_profile(user_id, updates)

        # Invalidate cache (will reload on next access)
        self.redis.delete(f"profile:{user_id}")
```

---

### Pattern 3: Background Summarization

**Summarize conversations asynchronously**

```python
import asyncio
from queue import Queue

class BackgroundSummarizer:
    """Summarize sessions in background without blocking"""

    def __init__(self, llm):
        self.llm = llm
        self.queue = Queue()
        self.running = False

    def start(self):
        """Start background worker"""
        self.running = True
        asyncio.create_task(self._worker())

    async def _worker(self):
        """Process summarization queue"""
        while self.running:
            if not self.queue.empty():
                session = self.queue.get()
                summary = await self._summarize_async(session)
                self._save_summary(session['session_id'], summary)
            else:
                await asyncio.sleep(1)

    def queue_session(self, session: Dict):
        """Add session to summarization queue"""
        self.queue.put(session)

    async def _summarize_async(self, session: Dict) -> str:
        """Async summarization"""
        # Use async LLM call
        return await self.llm.generate_async(f"Summarize: {session}")

    def stop(self):
        """Stop background worker"""
        self.running = False
```

---

## Best Practices

### 1. Context Window Efficiency

✅ **DO**:
- Prioritize recent messages over old ones
- Use semantic search for relevant retrieval
- Compress repetitive information
- Set token budgets for each component
- Monitor actual token usage vs budget

❌ **DON'T**:
- Include entire conversation every time
- Retrieve irrelevant RAG results
- Duplicate information across components
- Assume "more context = better"

---

### 2. Memory Persistence

✅ **DO**:
- Save session summaries, not full transcripts (unless needed)
- Use vector embeddings for semantic retrieval
- Implement TTL (time-to-live) for old data
- Back up user profiles regularly
- Version your data schemas

❌ **DON'T**:
- Store sensitive information unencrypted
- Keep conversations forever without user consent
- Ignore GDPR/privacy requirements
- Let memory databases grow unbounded

---

### 3. Performance Optimization

✅ **DO**:
- Cache frequently accessed data (Redis)
- Use database indexes on user_id, session_id
- Batch summarization operations
- Lazy-load heavy components
- Profile token usage and optimize

❌ **DON'T**:
- Load all user history on every query
- Run expensive operations in request path
- Generate embeddings synchronously
- Skip monitoring memory/latency

---

### 4. User Experience

✅ **DO**:
- Reference past conversations when relevant
- Acknowledge user's learning progress
- Adapt difficulty to skill level
- Provide continuity across sessions
- Let users delete their data

❌ **DON'T**:
- Surprise users with remembered information
- Confuse current query with past queries
- Make assumptions based on old data
- Force personalization if user prefers stateless

---

## Poker Advisor Application

### Current State

Our poker advisor is **mostly stateless**:
- ❌ No memory of past conversations
- ❌ No user profiles
- ❌ No learning progress tracking
- ✅ Has session memory (current conversation only)

### Recommended Architecture

```python
class PokerAdvisorWithMemory:
    """
    Enhanced poker advisor with full memory system
    """

    def __init__(self, user_id: str):
        self.user_id = user_id

        # Memory system
        self.memory = HybridMemorySystem(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            config={
                'db': get_database_connection(),
                'vector_store': get_pinecone_client(),
                'embeddings': get_embedding_model(),
                'context_budget': 8000
            }
        )

        # Core advisor
        self.advisor = PokerAdvisor()

    def get_advice(self, query: str) -> str:
        """
        Get advice with full context awareness
        """

        # 1. Build context from all memory sources
        context = self.memory.build_context_for_query(query)

        # 2. Get user's skill level to adjust response
        skill_level = self.memory.profile.get_skill_level()

        # 3. Check if we've discussed this before
        past_episodes = self.memory.episodes.recall_similar_episodes(
            query, self.user_id, k=2
        )

        # 4. Enhance system prompt with personalization
        personalized_prompt = f"""
        {self.advisor.SYSTEM_PROMPT}

        === USER CONTEXT ===
        Skill Level: {skill_level}

        Past Conversations:
        {self._format_past_episodes(past_episodes)}

        Current Session Context:
        {context}
        """

        # 5. Get advice
        response = self.advisor.get_advice(query, context=personalized_prompt)

        # 6. Record interaction
        self.memory.add_interaction(query, response)

        return response

    def end_session(self):
        """Save session when user leaves"""
        self.memory.end_session(self.advisor.llm)

    def _format_past_episodes(self, episodes: List[Dict]) -> str:
        if not episodes:
            return "This is the first time discussing this topic."

        formatted = ""
        for ep in episodes:
            formatted += f"""
            [{ep['timestamp'].strftime('%Y-%m-%d')}]
            Summary: {ep['summary']}
            Concepts Covered: {ep['metadata'].get('concepts_learned', [])}
            """
        return formatted
```

### Example Conversation Flow

**Without Memory** (current):
```
User: "What are pot odds?"
Bot: "Pot odds are the ratio of the pot size to the cost of calling..."

[2 weeks later]
User: "What are pot odds?"
Bot: "Pot odds are the ratio of the pot size to the cost of calling..."
```

**With Memory** (proposed):
```
User: "What are pot odds?"
Bot: "Pot odds are the ratio of the pot size to the cost of calling..."
[Stores: User asked about pot odds, beginner level explanation given]

[2 weeks later]
User: "What are pot odds?"
Bot: "We covered pot odds on [date]. You seemed to understand the basic
     concept of comparing pot size to call amount. Would you like to:
     1. Review the basics, or
     2. Move to advanced topics like implied odds?"
[Retrieves past episode, recognizes repeat question, offers progression]
```

---

## Common Pitfalls

### Pitfall 1: Memory Overload

**Problem**: Trying to include too much context.

**Symptom**:
```python
# BAD: Including everything
context = {
    'all_past_sessions': load_all_sessions(),  # 100+ sessions!
    'entire_knowledge_base': load_all_docs(),  # 10MB of text!
    'full_user_history': load_all_actions()    # Years of data!
}
```

**Solution**: Be selective.
```python
# GOOD: Selective retrieval
context = {
    'recent_session': get_recent_messages(n=10),
    'relevant_knowledge': semantic_search(query, k=3),
    'key_user_facts': get_profile_summary()
}
```

---

### Pitfall 2: Stale Context

**Problem**: Using outdated information.

**Symptom**:
```python
# BAD: User skill level from 6 months ago
if user.skill_level == 'beginner':  # Cached from first session!
    explain_basic_concepts()
```

**Solution**: Update and timestamp.
```python
# GOOD: Recent skill assessment
skill = assess_current_skill_level(user, days=7)
if skill == 'beginner':
    explain_basic_concepts()
```

---

### Pitfall 3: Privacy Violations

**Problem**: Storing too much personal information.

**Symptom**:
```python
# BAD: Storing everything forever
store_conversation({
    'user_name': "John Doe",
    'credit_card': "...",  # Never store PII!
    'full_transcript': "..."  # Permanent storage
})
```

**Solution**: Anonymize and expire.
```python
# GOOD: Privacy-conscious storage
store_conversation({
    'user_id': hash(user_id),  # Anonymized
    'summary': summarize(transcript),  # Not full text
    'expires_at': now() + timedelta(days=90)  # Auto-delete
})
```

---

### Pitfall 4: Confusing Current with Past

**Problem**: Mixing current game state with historical data.

**Symptom**:
```python
# BAD: Ambiguous retrieval
context = search_memory("flush draw")  # Returns old hand? Current hand?
```

**Solution**: Clear namespace.
```python
# GOOD: Explicit separation
current_hand = get_game_state()  # Current session
past_similar = search_episodes("flush draw", exclude=current_session_id)
```

---

## Summary

### Context Window Management

| Strategy | Complexity | Performance | Use Case |
|----------|-----------|-------------|----------|
| Sliding Window | Low | Fast | Simple chat |
| Summarization | Medium | Medium | Long conversations |
| Hierarchical | High | Best | Complex domains |
| Importance-Based | Medium | Good | Structured conversations |
| Token Budget | Medium | Predictable | Production systems |

### Memory Systems

| Type | Persistence | Retrieval | Use Case |
|------|------------|-----------|----------|
| Session | Temporary | Direct | Current conversation |
| Profile | Permanent | Direct | User preferences |
| Episodic | Permanent | Semantic | Past conversations |
| Hybrid | Mixed | Multi-strategy | Full-featured systems |

### Key Takeaways

1. **Context is expensive** - Be selective, not exhaustive
2. **Memory is powerful** - Enables personalization and continuity
3. **Balance is critical** - Too much context → diluted, too little → uninformed
4. **User privacy matters** - Store only what's needed, with consent
5. **Monitor and optimize** - Profile token usage, latency, and accuracy

---

## Further Reading

- [LangChain Memory Documentation](https://python.langchain.com/docs/modules/memory/)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Vector Databases for LLM Applications](https://www.pinecone.io/learn/)
- [Building LLM Applications for Production](https://huyenchip.com/2023/04/11/llm-engineering.html)

---

**Last Updated**: 2025-11-09
