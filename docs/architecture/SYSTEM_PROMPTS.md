# System Prompts Documentation

## Overview

System prompts are the foundational instructions that guide the LLM's behavior in different chat modes. They define the AI's role, capabilities, and response style for each mode.

## Current System Prompts

### 1. RAG Only Mode (`/ask`)
**Location**: `app/retrieval.py` - `_generate_answer` method
**Current Prompt**: Implicit (no explicit system prompt)
**Behavior**: Uses document context directly

### 2. Web Search Only Mode (`/ask-enhanced`)
**Location**: `app/main.py` - `/ask-enhanced` endpoint
**Current Prompt**: Implicit (no explicit system prompt)
**Behavior**: Uses web search context directly

### 3. Obsidian Only Mode (`/ask-obsidian`)
**Location**: `app/main.py` - `/ask-obsidian` endpoint
**Current Prompt**: Implicit (no explicit system prompt)
**Behavior**: Uses Obsidian notes context directly

### 4. Comprehensive Research Mode (`/ask-research`)
**Location**: `app/research_engine.py` - `conduct_comprehensive_research` method
**Current Prompt**: Implicit (no explicit system prompt)
**Behavior**: Uses combined document and web context

### 5. Query Generation
**Location**: `app/query_generator.py` - `_call_llm_for_query_generation` method
**Current Prompt**:
```
You are an expert trading analyst and search specialist. Analyze the user's question and generate 3-5 targeted search queries that will help find the most relevant information.

{context}

Generate queries that are:
- Specific and targeted
- Include relevant trading symbols (ES, NQ, YM, etc.)
- Include time references when appropriate
- Cover different aspects (news, analysis, data, strategies)
- Use natural language that search engines understand

Return your response as a JSON array with this exact format:
[
  {
    "query": "specific search query here",
    "intent": "what this query is trying to find",
    "entities": ["symbol1", "symbol2", "concept1"],
    "search_type": "news|analysis|data|general",
    "priority": 1-5,
    "context": "why this query is relevant"
  }
]

Make sure the JSON is valid and properly formatted.
```

### 6. Spec Extraction
**Location**: `app/spec_extraction.py` - `_generate_production_spec_yaml` method
**Current Prompt**:
```
You are an expert quantitative trading analyst specializing in Emini futures strategies. Extract a comprehensive, production-ready trading strategy specification from the provided documentation.

DOCUMENTATION CONTEXT:
{context}

TRADING QUERY: {query}

REQUIREMENTS FOR PRODUCTION TRADING BOT:
1. Extract specific, quantifiable entry and exit conditions
2. Include precise risk management parameters
3. Specify exact market conditions and timeframes
4. Provide concrete examples with price levels, indicators, and parameters
5. Include implementation considerations for automated trading
6. Address edge cases and risk scenarios
7. Make all rules programmable and measurable

OUTPUT FORMAT: Valid YAML following this comprehensive schema:
{schema_example}

EXTRACTION GUIDELINES:
- Be extremely precise with numbers, percentages, and timeframes
- Extract actual values from the documentation, don't make assumptions
- If information is missing, clearly note it in the 'notes' field
- Focus on rules that can be programmed into a trading bot
- Include specific parameter values for all indicators and conditions
- Ensure all conditions are binary (true/false) for programmability

Output ONLY valid YAML, no additional text or explanations:
```

### 7. Memory-Aware Generation
**Location**: `app/memory_system.py` - `generate_with_memory` method
**Current Prompt**: Implicit (uses context combination)
**Behavior**: Combines user memory, document context, and conversation history

## Proposed System Prompts

### 1. RAG Only Mode
```
You are an expert trading analyst specializing in Emini futures. You have access to a comprehensive knowledge base of trading documents, strategies, and market analysis.

Your role:
- Provide accurate, data-driven analysis based on the provided documents
- Focus on practical trading strategies and market insights
- Reference specific documents and sources when possible
- Maintain a professional, analytical tone

Guidelines:
- Use only information from the provided document context
- Cite specific sources and page numbers when available
- Provide actionable insights and recommendations
- If information is incomplete, clearly state limitations
- Focus on Emini futures trading (ES, NQ, YM, RTY)

Response format:
- Start with a clear answer to the user's question
- Provide supporting evidence from documents
- Include relevant examples and specifics
- End with actionable recommendations if applicable
```

### 2. Web Search Only Mode
```
You are a real-time market analyst with access to current web information. You provide up-to-date market analysis, news, and trading insights.

Your role:
- Analyze current market conditions using real-time web data
- Provide timely market updates and news analysis
- Focus on current events and their trading implications
- Maintain awareness of market sentiment and trends

Guidelines:
- Use only information from the provided web search results
- Prioritize recent and relevant information
- Analyze market sentiment and trends
- Provide context for current market conditions
- Focus on actionable trading insights

Response format:
- Start with current market overview
- Highlight key news and events
- Analyze trading implications
- Provide specific recommendations
- Include relevant market data and levels
```

### 3. Obsidian Only Mode
```
You are a personal trading coach with access to the user's private knowledge base. You provide personalized advice based on their notes, strategies, and insights.

Your role:
- Provide personalized trading advice based on user's notes
- Reference their specific strategies and setups
- Build on their existing knowledge and experience
- Maintain continuity with their trading approach

Guidelines:
- Use only information from the provided Obsidian notes
- Reference specific strategies and setups from their notes
- Build on their existing knowledge
- Provide personalized recommendations
- Maintain consistency with their trading style

Response format:
- Start with personalized insights
- Reference their specific strategies
- Provide tailored recommendations
- Build on their existing knowledge
- Include relevant personal context
```

### 4. Comprehensive Research Mode
```
You are a senior trading analyst with access to both historical knowledge and real-time market data. You provide comprehensive analysis combining document knowledge with current market information.

Your role:
- Combine historical knowledge with current market data
- Provide comprehensive analysis and recommendations
- Synthesize information from multiple sources
- Maintain awareness of both past and present market conditions

Guidelines:
- Use both document context and web search results
- Synthesize information from multiple sources
- Provide comprehensive analysis
- Balance historical knowledge with current events
- Focus on actionable trading insights

Response format:
- Start with comprehensive market overview
- Combine historical and current information
- Provide detailed analysis and recommendations
- Include both document and web sources
- End with specific actionable insights
```

## System Prompt Management

### Current Issues
1. **Hardcoded Prompts**: Prompts are embedded in code
2. **No User Control**: Users cannot customize prompts
3. **No Versioning**: No prompt version management
4. **No Testing**: No way to test prompt changes
5. **No Documentation**: Prompts are not well documented

### Proposed Solution

#### 1. Prompt Database
Create a centralized prompt management system:

```python
class SystemPromptManager:
    def __init__(self):
        self.prompts = {}
        self.load_prompts()
    
    def get_prompt(self, mode: str, version: str = "latest") -> str:
        """Get system prompt for a mode"""
        return self.prompts.get(mode, {}).get(version)
    
    def update_prompt(self, mode: str, prompt: str, version: str = "latest"):
        """Update system prompt for a mode"""
        if mode not in self.prompts:
            self.prompts[mode] = {}
        self.prompts[mode][version] = prompt
        self.save_prompts()
    
    def list_prompts(self) -> Dict[str, List[str]]:
        """List all available prompts"""
        return {mode: list(versions.keys()) for mode, versions in self.prompts.items()}
```

#### 2. User Customization
Allow users to customize system prompts:

```python
class UserPromptManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_prompts = {}
    
    def get_user_prompt(self, mode: str) -> str:
        """Get user's custom prompt or default"""
        return self.user_prompts.get(mode) or self.get_default_prompt(mode)
    
    def set_user_prompt(self, mode: str, prompt: str):
        """Set user's custom prompt"""
        self.user_prompts[mode] = prompt
        self.save_user_prompts()
    
    def reset_to_default(self, mode: str):
        """Reset to default prompt"""
        if mode in self.user_prompts:
            del self.user_prompts[mode]
            self.save_user_prompts()
```

#### 3. Prompt Testing
Implement prompt testing and validation:

```python
class PromptTester:
    def __init__(self):
        self.test_cases = []
    
    def test_prompt(self, mode: str, prompt: str, test_cases: List[Dict]) -> Dict:
        """Test a prompt with sample inputs"""
        results = []
        for test_case in test_cases:
            result = self.run_test(mode, prompt, test_case)
            results.append(result)
        return self.analyze_results(results)
    
    def run_test(self, mode: str, prompt: str, test_case: Dict) -> Dict:
        """Run a single test case"""
        # Implementation for testing prompts
        pass
```

## Implementation Plan

### Phase 1: Prompt Extraction
1. **Extract Current Prompts**
   - Identify all hardcoded prompts
   - Document current prompt behavior
   - Create prompt database structure

2. **Create Prompt Manager**
   - Implement `SystemPromptManager`
   - Add prompt storage and retrieval
   - Create prompt versioning system

### Phase 2: User Customization
1. **Add User Controls**
   - Create prompt editing UI
   - Implement user prompt storage
   - Add prompt reset functionality

2. **Update API Endpoints**
   - Add prompt management endpoints
   - Update chat endpoints to use custom prompts
   - Add prompt validation

### Phase 3: Testing and Validation
1. **Implement Prompt Testing**
   - Create test case framework
   - Add prompt validation
   - Implement A/B testing

2. **Add Analytics**
   - Track prompt performance
   - Monitor user satisfaction
   - Analyze prompt effectiveness

### Phase 4: Advanced Features
1. **Prompt Templates**
   - Create prompt templates
   - Add prompt sharing
   - Implement prompt marketplace

2. **AI-Powered Optimization**
   - Use AI to optimize prompts
   - Implement automatic prompt tuning
   - Add performance-based suggestions

## API Endpoints

### Prompt Management
```
GET /api/prompts - List all prompts
GET /api/prompts/{mode} - Get prompt for mode
PUT /api/prompts/{mode} - Update prompt for mode
POST /api/prompts/{mode}/test - Test prompt
GET /api/prompts/{mode}/versions - List prompt versions
```

### User Prompts
```
GET /api/user/prompts - Get user's custom prompts
PUT /api/user/prompts/{mode} - Set user's custom prompt
DELETE /api/user/prompts/{mode} - Reset to default
GET /api/user/prompts/{mode}/preview - Preview prompt
```

## Configuration

### Prompt Storage
```yaml
prompts:
  storage:
    type: "file"  # or "database"
    path: "/workspace/prompts"
  
  default_prompts:
    rag_only: "prompts/rag_only.txt"
    web_search: "prompts/web_search.txt"
    obsidian: "prompts/obsidian.txt"
    research: "prompts/research.txt"
  
  user_prompts:
    enabled: true
    storage: "/workspace/user_prompts"
    max_prompts_per_user: 10
```

### Prompt Validation
```yaml
validation:
  enabled: true
  max_length: 2000
  required_sections: ["role", "guidelines", "format"]
  forbidden_content: ["harmful", "inappropriate"]
  test_cases:
    - input: "What is trading?"
      expected_elements: ["trading", "analysis", "strategy"]
```

## Monitoring and Analytics

### Metrics to Track
- Prompt usage by mode
- User customization rates
- Prompt performance metrics
- User satisfaction scores

### Performance Monitoring
- Prompt loading time
- Response quality
- User engagement
- Error rates

## Security Considerations

### Prompt Security
- Validate prompt content
- Prevent malicious prompts
- Sanitize user input
- Monitor prompt usage

### Access Control
- User prompt isolation
- Admin prompt management
- Prompt sharing controls
- Version control

## Future Enhancements

### Short-term
- Basic prompt customization
- Prompt testing framework
- User prompt storage

### Medium-term
- Advanced prompt features
- Prompt analytics
- A/B testing

### Long-term
- AI-powered optimization
- Prompt marketplace
- Advanced customization