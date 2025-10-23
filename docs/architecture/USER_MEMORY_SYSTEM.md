# User Memory System Documentation

## Overview

The EminiPlayer User Memory System provides persistent storage and retrieval of user-specific information across chat sessions. It enables the system to remember user preferences, chat history, trading strategies, and key insights.

## Architecture

### Storage Technology
- **Primary Storage**: File-based JSON storage
- **Location**: `/workspace/user_memory/`
- **Format**: JSON files organized by user ID and category
- **Persistence**: Disk-based, survives container restarts

### Data Structure
```
/workspace/user_memory/
├── {user_id}/
│   ├── user_preferences.json
│   ├── chat_history.json
│   ├── trading_strategies.json
│   ├── key_insights.json
│   └── conversation_context.json
```

## Memory Categories

### 1. User Preferences (`user_preferences.json`)
**Purpose**: Store user-specific settings and preferences
**Content**:
- Model preferences
- Temperature settings
- Token limits
- UI preferences
- Feature toggles

**Example**:
```json
{
  "selected_model": "qwen2.5-coder:14b",
  "temperature": 0.1,
  "max_tokens": 8000,
  "theme": "dark",
  "updated_at": 1698000000
}
```

### 2. Chat History (`chat_history.json`)
**Purpose**: Store conversation history and metadata
**Content**:
- Chat sessions
- Message history
- Timestamps
- Chat metadata

**Example**:
```json
{
  "chat_123": {
    "title": "Trading Strategy Discussion",
    "messages": [...],
    "created_at": 1698000000,
    "updated_at": 1698000000
  }
}
```

### 3. Trading Strategies (`trading_strategies.json`)
**Purpose**: Store user's trading strategies and setups
**Content**:
- Strategy definitions
- Entry/exit conditions
- Risk parameters
- Performance metrics

**Example**:
```json
{
  "strategy_456": {
    "name": "E-mini Fade Strategy",
    "description": "Fade moves at key levels",
    "entry_conditions": [...],
    "exit_conditions": [...],
    "risk_management": {...},
    "created_at": 1698000000
  }
}
```

### 4. Key Insights (`key_insights.json`)
**Purpose**: Store important insights and learnings
**Content**:
- Key takeaways
- Important concepts
- Learning notes
- Categorized insights

**Example**:
```json
{
  "insight_789": {
    "content": "Market structure analysis shows...",
    "category": "strategy_discussion",
    "importance": 0.8,
    "tags": ["market_structure", "analysis"],
    "created_at": 1698000000
  }
}
```

### 5. Conversation Context (`conversation_context.json`)
**Purpose**: Store context for ongoing conversations
**Content**:
- Current conversation state
- Context variables
- Session data
- Temporary information

**Example**:
```json
{
  "chat_123": {
    "current_topic": "trading_strategy",
    "context_variables": {...},
    "session_data": {...},
    "updated_at": 1698000000
  }
}
```

## API Endpoints

### Memory Management
- `GET /memory/preferences` - Get user preferences
- `POST /memory/preferences` - Update user preferences
- `GET /memory/insights` - Get key insights
- `POST /memory/insights` - Store new insight
- `GET /memory/strategies` - Get trading strategies
- `POST /memory/strategies` - Store new strategy
- `DELETE /memory/clear` - Clear all memory
- `GET /memory/export` - Export memory data

### Memory Integration
- Memory context is automatically included in all chat responses
- Memory is updated based on conversation content
- Insights are extracted and stored automatically

## Usage Examples

### Storing User Preferences
```python
# Store a user preference
user_memory.store_preference("user123", "selected_model", "qwen2.5-coder:14b")
user_memory.store_preference("user123", "temperature", 0.1)

# Retrieve a preference
model = user_memory.get_preference("user123", "selected_model", "default-model")
```

### Storing Chat Context
```python
# Store chat context
context = {
    "current_topic": "trading_strategy",
    "key_points": ["entry conditions", "risk management"],
    "user_goals": ["learn fade strategy"]
}
user_memory.store_chat_context("user123", "chat_456", context)

# Retrieve chat context
context = user_memory.get_chat_context("user123", "chat_456")
```

### Storing Strategy Insights
```python
# Store a trading strategy insight
user_memory.store_strategy_insight(
    "user123",
    "E-mini Fade Strategy",
    "Key levels at 4500 and 4520 show strong resistance",
    importance=0.9
)

# Store a key insight
user_memory.store_key_insight(
    "user123",
    "Market structure analysis shows consolidation pattern",
    "strategy_discussion"
)
```

## Memory Retrieval

### Automatic Context Integration
The memory system automatically provides context for chat responses:

```python
# Memory context is automatically included
memory_context = user_memory.get_memory_context("user123", query)
full_context = f"""
USER MEMORY CONTEXT:
{memory_context}

RETRIEVED DOCUMENT CONTEXT:
{document_context}

USER QUESTION: {query}
"""
```

### Memory Search
```python
# Search for relevant insights
insights = user_memory.search_insights("user123", "trading strategy")
strategies = user_memory.search_strategies("user123", "fade")
```

## Memory Management

### Clearing Memory
```python
# Clear specific category
user_memory.clear_category("user123", "insights")

# Clear all memory
user_memory.clear_all_memory("user123")
```

### Memory Export
```python
# Export all memory data
memory_data = user_memory.export_memory("user123")

# Export specific category
insights = user_memory.export_category("user123", "insights")
```

## Security and Privacy

### Data Protection
- User data is isolated by user ID
- No cross-user data access
- Secure file permissions
- Data encryption at rest (if configured)

### Privacy Controls
- Users can clear their own memory
- Memory export includes all user data
- No data sharing between users
- Local storage only (no external services)

## Performance Considerations

### Storage Optimization
- JSON files are compressed when possible
- Old data can be archived
- Memory usage is monitored
- Cleanup routines for expired data

### Retrieval Performance
- Memory context is cached during chat sessions
- Lazy loading for large memory files
- Indexing for fast searches
- Background processing for insights

## Monitoring and Analytics

### Memory Statistics
- Total memory size per user
- Memory category distribution
- Memory growth over time
- Most accessed insights

### Performance Metrics
- Memory retrieval time
- Memory storage time
- Memory search performance
- Memory cleanup efficiency

## Troubleshooting

### Common Issues
1. **Memory not persisting**: Check file permissions
2. **Memory not loading**: Verify JSON format
3. **Memory corruption**: Use backup/restore
4. **Performance issues**: Check disk space and I/O

### Debug Commands
```bash
# Check memory directory
ls -la /workspace/user_memory/

# Check user memory
ls -la /workspace/user_memory/{user_id}/

# Verify JSON files
python -m json.tool /workspace/user_memory/{user_id}/user_preferences.json
```

## Future Enhancements

### Planned Features
- [ ] Memory search and filtering
- [ ] Memory analytics dashboard
- [ ] Memory backup/restore UI
- [ ] Memory sharing between users
- [ ] Memory templates and presets
- [ ] Memory performance optimization
- [ ] Memory data visualization
- [ ] Memory export formats (CSV, PDF)