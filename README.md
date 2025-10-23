# EminiPlayer - Advanced Trading RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system designed for trading and financial analysis, combining document knowledge, web search, and personal notes to provide intelligent responses.

## 🚀 Features

### Chat Modes
- **RAG Only**: Document-based responses from PDFs, video transcripts, and processed content
- **Web Search Only**: Real-time web search results for current market information
- **Obsidian Only**: Personal knowledge base integration for personalized advice
- **Comprehensive Research**: Combined document and web search for comprehensive analysis

### Advanced Capabilities
- **User Memory System**: Persistent storage of user preferences, chat history, and insights
- **Model Switching**: Change AI models mid-conversation
- **Smart Chat Naming**: AI-powered chat title generation
- **Response Time Tracking**: Monitor and display response times
- **Export Functionality**: Export chats in Markdown format
- **Customizable System Prompts**: User-editable system prompts for each mode

### Technical Features
- **Docker-based Deployment**: Containerized services with Docker Compose
- **Cloudflare Integration**: Secure external access via Cloudflare Tunnels
- **Vector Database**: ChromaDB for efficient document retrieval
- **Multiple LLM Support**: Ollama integration with various models
- **Real-time Web Search**: SearXNG integration for current information
- **Personal Knowledge**: Obsidian MCP client for personal notes

## 📁 Project Structure

```
EminiPlayer/
├── app/                          # Backend FastAPI application
│   ├── auth.py                   # Authentication system
│   ├── memory_system.py          # User memory management
│   ├── retrieval.py              # RAG retrieval system
│   ├── web_search.py             # Web search integration
│   ├── obsidian_mcp_client.py    # Obsidian integration
│   └── main.py                   # Main FastAPI application
├── frontend/                     # Next.js frontend
│   ├── components/               # React components
│   ├── lib/                      # Utility libraries
│   └── app/                      # Next.js app directory
├── docs/                         # Comprehensive documentation
│   ├── architecture/             # System architecture docs
│   ├── guides/                   # User guides
│   ├── api/                      # API documentation
│   └── testing/                  # Testing documentation
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── scripts/                      # Utility scripts
├── config/                       # Configuration files
└── .github/workflows/            # GitHub Actions CI/CD
```

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.10+
- Ollama (for LLM inference)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/EminiPlayer.git
   cd EminiPlayer
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001 (internal)

### Configuration

1. **Environment Variables**
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # Edit configuration
   nano .env
   ```

2. **Ollama Setup**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull required models
   ollama pull qwen2.5-coder:14b
   ```

3. **Obsidian Setup** (Optional)
   - Install Obsidian
   - Set up MCP server
   - Configure vault path

## 📚 Documentation

### Architecture
- [System Architecture](docs/architecture/ARCHITECTURE.md)
- [User Memory System](docs/architecture/USER_MEMORY_SYSTEM.md)
- [Chat System](docs/architecture/CHAT_SYSTEM.md)
- [System Prompts](docs/architecture/SYSTEM_PROMPTS.md)

### Guides
- [Quick Start Guide](docs/guides/QUICKSTART.md)
- [Setup Instructions](docs/guides/SETUP.md)
- [Deployment Guide](docs/guides/DEPLOYMENT.md)

### API Reference
- [API Documentation](docs/api/API.md)
- [Authentication](docs/api/AUTH.md)
- [Chat Endpoints](docs/api/CHAT.md)

### Testing
- [QA Automation](docs/testing/QA_AUTOMATION.md)
- [Test Suite](docs/testing/TEST_SUITE.md)
- [Performance Testing](docs/testing/PERFORMANCE.md)

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/e2e/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API and service integration
- **End-to-End Tests**: Full user workflow testing
- **Performance Tests**: Response time and load testing

## 🚀 Deployment

### Production Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Configure Cloudflare Tunnel
cloudflared tunnel create eminiplayer
cloudflared tunnel route dns eminiplayer emini.riffyx.com
```

### Environment Configuration
- **Development**: Local Docker containers
- **Production**: Cloudflare Tunnel + Docker
- **Staging**: Separate environment for testing

## 🔧 Development

### Adding New Features
1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Run test suite
5. Submit pull request

### Code Quality
- Follow PEP 8 for Python
- Use TypeScript for frontend
- Add comprehensive tests
- Update documentation
- Follow security best practices

### Testing Requirements
- All new features must include tests
- Test coverage must be >80%
- All tests must pass before merge
- Performance tests for critical paths

## 📊 Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: Built-in health monitoring
- Database: Connection monitoring
- External Services: Service availability

### Metrics
- Response times by mode
- User engagement metrics
- Memory usage statistics
- Error rates and patterns

### Logging
- Structured logging throughout
- Error tracking and alerting
- Performance monitoring
- Security event logging

## 🔒 Security

### Authentication
- JWT-based authentication
- Secure token storage
- Session management
- User data isolation

### Data Protection
- Encrypted data storage
- Secure API communication
- User data privacy
- Regular security scans

### Best Practices
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Set up development environment
4. Make changes with tests
5. Submit pull request

### Code Standards
- Follow existing code style
- Add comprehensive tests
- Update documentation
- Include examples
- Follow security guidelines

### Pull Request Process
1. Ensure all tests pass
2. Update documentation
3. Add changelog entry
4. Request review
5. Address feedback

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Ollama for LLM inference
- SearXNG for web search
- Obsidian for personal knowledge management
- FastAPI for the backend framework
- Next.js for the frontend framework

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/EminiPlayer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/EminiPlayer/discussions)

## 🔄 Changelog

### Recent Updates
- ✅ Fixed data source exclusivity issues
- ✅ Implemented comprehensive test suite
- ✅ Added user memory system
- ✅ Created extensive documentation
- ✅ Set up QA automation

### Upcoming Features
- 🔄 Model switching mid-chat
- 🔄 Chat export functionality
- 🔄 Response time measurement
- 🔄 Smart chat naming
- 🔄 System prompt customization

---

**EminiPlayer** - Advanced Trading RAG System for Intelligent Financial Analysis