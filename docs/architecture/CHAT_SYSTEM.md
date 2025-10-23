# Chat System Documentation

## Overview

The EminiPlayer Chat System provides a comprehensive chat interface with multiple modes, model switching, and advanced features for trading and financial analysis.

## Current Implementation

### Chat Modes
1. **RAG Only** - Document-based responses
2. **Web Search Only** - Web search results
3. **Obsidian Only** - Personal notes
4. **Comprehensive Research** - Documents + Web search

### Chat Management
- **Naming**: LLM-generated titles with fallback
- **Storage**: In-memory with persistence
- **History**: Full conversation history
- **Export**: Not currently implemented

## Architecture

### Frontend Components
```
ChatInterface.tsx
├── ChatControls.tsx (Mode selection)
├── MessageList.tsx (Message display)
├── MessageInput.tsx (Input handling)
└── Sidebar.tsx (Chat management)
```

### Backend Integration
```
ChatInterface → API Routes → Backend Endpoints
├── /api/ask (RAG Only)
├── /api/ask-enhanced (Web Search)
├── /api/ask-obsidian (Obsidian)
└── /api/ask-research (Comprehensive)
```

## Current Features

### Chat Creation
- **Auto-naming**: Uses LLM to generate titles
- **Fallback naming**: First 4 words of prompt
- **Chat persistence**: Stored in application state
- **Chat switching**: Seamless between chats

### Message Handling
- **Real-time updates**: Streaming responses
- **Processing indicators**: Visual feedback
- **Error handling**: Retry mechanisms
- **Message history**: Full conversation context

### Model Management
- **Model selection**: Global model setting
- **Model switching**: Not supported mid-chat
- **Model persistence**: Stored in user preferences

## Planned Enhancements

### 1. Model Switching Mid-Chat
**Current State**: Not supported
**Planned Implementation**:
- Add model selector to chat interface
- Update chat history to track model changes
- Maintain conversation context across model switches
- Add model indicators in message UI

**Technical Requirements**:
- Update `ChatInterface.tsx` with model selector
- Modify `store.ts` to track model per message
- Update API calls to include model parameter
- Add model change indicators

### 2. Chat Export (Markdown)
**Current State**: Not implemented
**Planned Implementation**:
- Individual chat export
- Bulk export functionality
- Markdown formatting
- Export scheduling

**Technical Requirements**:
- Create export service
- Add export UI components
- Implement markdown formatting
- Add export API endpoints

### 3. Response Time Measurement
**Current State**: Not measured
**Planned Implementation**:
- Measure response times for each mode
- Display average response times
- Add response time analytics
- Set user expectations

**Technical Requirements**:
- Add timing to API endpoints
- Create metrics collection system
- Add UI components for display
- Implement analytics dashboard

### 4. Smart Chat Naming
**Current State**: Basic LLM naming
**Planned Implementation**:
- Use Llama3.2 for better naming
- Extract topics and themes
- Create naming templates
- Add manual naming override

**Technical Requirements**:
- Integrate Llama3.2 model
- Create topic extraction service
- Update naming logic
- Add manual naming UI

### 5. Response Formatting
**Current State**: Plain text
**Planned Implementation**:
- Markdown rendering
- Code syntax highlighting
- Response templates
- Formatting options

**Technical Requirements**:
- Add markdown renderer
- Implement syntax highlighting
- Create response templates
- Add formatting controls

## Implementation Plan

### Phase 1: Model Switching
1. **Update Chat Interface**
   - Add model selector component
   - Update message display to show model
   - Add model change indicators

2. **Update State Management**
   - Track model per message
   - Handle model switching logic
   - Persist model changes

3. **Update API Integration**
   - Pass model parameter to API
   - Handle model-specific responses
   - Update error handling

### Phase 2: Chat Export
1. **Create Export Service**
   - Markdown formatting
   - Export templates
   - File generation

2. **Add Export UI**
   - Export buttons
   - Export options
   - Progress indicators

3. **Implement Export API**
   - Individual chat export
   - Bulk export
   - Export scheduling

### Phase 3: Response Time Measurement
1. **Add Timing Infrastructure**
   - API endpoint timing
   - Metrics collection
   - Performance monitoring

2. **Create Analytics System**
   - Response time tracking
   - Average calculations
   - Performance reports

3. **Update UI**
   - Response time display
   - Performance indicators
   - User expectations

### Phase 4: Smart Naming
1. **Integrate Llama3.2**
   - Model integration
   - Topic extraction
   - Naming generation

2. **Update Naming Logic**
   - Smart naming algorithm
   - Template system
   - Manual override

3. **Enhance UI**
   - Naming preview
   - Manual naming
   - Naming history

### Phase 5: Response Formatting
1. **Add Markdown Support**
   - Markdown renderer
   - Syntax highlighting
   - Formatting options

2. **Create Templates**
   - Response templates
   - Formatting presets
   - Custom formatting

3. **Update UI**
   - Formatting controls
   - Preview mode
   - Formatting options

## Technical Specifications

### API Endpoints
```
GET /api/chats - List all chats
POST /api/chats - Create new chat
GET /api/chats/{id} - Get chat details
PUT /api/chats/{id} - Update chat
DELETE /api/chats/{id} - Delete chat
POST /api/chats/{id}/export - Export chat
POST /api/chats/{id}/rename - Rename chat
```

### Data Models
```typescript
interface Chat {
  id: string
  title: string
  messages: Message[]
  model: string
  mode: string
  createdAt: string
  updatedAt: string
  responseTime?: number
}

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  model: string
  timestamp: string
  responseTime?: number
  isProcessing?: boolean
}
```

### State Management
```typescript
interface ChatState {
  chats: Chat[]
  currentChatId: string | null
  messages: Message[]
  selectedModel: string
  selectedMode: string
  responseTimes: ResponseTimeMetrics
  exportOptions: ExportOptions
}
```

## Testing Strategy

### Unit Tests
- Chat creation and management
- Message handling
- Model switching
- Export functionality

### Integration Tests
- API endpoint testing
- State management testing
- UI component testing
- End-to-end chat flow

### Performance Tests
- Response time measurement
- Memory usage testing
- Load testing
- Stress testing

## Monitoring and Analytics

### Metrics to Track
- Response times by mode
- Model usage statistics
- Chat creation rates
- Export usage
- User engagement

### Performance Monitoring
- API response times
- Memory usage
- CPU usage
- Error rates

### User Analytics
- Chat patterns
- Mode preferences
- Model usage
- Export behavior

## Security Considerations

### Data Protection
- Chat data encryption
- User data isolation
- Secure export
- Data retention policies

### Privacy Controls
- Chat deletion
- Export restrictions
- Data sharing controls
- User consent

## Future Roadmap

### Short-term (1-2 months)
- Model switching implementation
- Basic chat export
- Response time measurement
- Smart naming

### Medium-term (3-6 months)
- Advanced export features
- Response formatting
- Performance optimization
- Analytics dashboard

### Long-term (6+ months)
- AI-powered chat features
- Advanced analytics
- Integration with external tools
- Mobile support