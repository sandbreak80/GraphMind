# 🎨 EminiPlayer RAG Frontend

A modern, feature-rich web interface for the EminiPlayer RAG system, built with Next.js 14, TypeScript, and Tailwind CSS.

## ✨ Features

### 🔐 Authentication & User Management
- **Session Management**: Persistent login sessions with secure token handling
- **User Profiles**: Customizable user settings and preferences
- **Access Control**: Role-based access to different features

### 💬 Advanced Chat Interface
- **Real-time Messaging**: Instant responses with streaming support
- **Chat History**: Persistent conversation history with search
- **Message Types**: Support for text, code, and markdown content
- **Typing Indicators**: Visual feedback during message generation

### 🤖 Model Management
- **Ollama Integration**: Direct integration with local Ollama models
- **Model Selection**: Switch between different models on the fly
- **Parameter Tuning**: Adjust temperature, max tokens, and other settings
- **Model Status**: Real-time model availability and performance metrics

### 🔧 Feature Toggles
- **RAG Toggle**: Enable/disable document knowledge base search
- **Obsidian Toggle**: Enable/disable personal note integration
- **Web Search Toggle**: Enable/disable real-time web search
- **Mode Selection**: Choose between QA, Spec generation, and Obsidian modes

### 🎨 Modern UI/UX
- **Dark/Light Theme**: Automatic theme switching with system preference detection
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Accessibility**: WCAG compliant with keyboard navigation
- **Animations**: Smooth transitions and micro-interactions

### 📊 Advanced Features
- **Source Attribution**: See exactly which documents/notes were used
- **Citation Management**: Expandable source details with relevance scores
- **Export Options**: Download conversations and generated content
- **Settings Panel**: Comprehensive configuration management

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Docker and Docker Compose
- EminiPlayer RAG backend running

### Development Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Access the Application**
   - Open http://localhost:3000 in your browser
   - The frontend will automatically connect to the RAG backend

### Production Setup

1. **Build and Deploy with Docker**
   ```bash
   docker compose up -d
   ```

2. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001

## 🏗️ Architecture

### Tech Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Zustand for lightweight state management
- **HTTP Client**: Axios with interceptors
- **UI Components**: Headless UI + custom components
- **Icons**: Heroicons for consistent iconography

### Project Structure
```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── globals.css        # Global styles
│   └── providers.tsx      # Context providers
├── components/            # Reusable UI components
│   ├── ChatInterface.tsx  # Main chat component
│   ├── MessageBubble.tsx  # Individual message component
│   ├── Sidebar.tsx        # Chat history sidebar
│   ├── SettingsModal.tsx  # Settings configuration
│   └── ...               # Other components
├── lib/                   # Utilities and configurations
│   ├── store.ts          # Zustand store
│   └── api.ts            # API client
└── ...                   # Configuration files
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001

# Optional: Custom API endpoints
NEXT_PUBLIC_OLLAMA_URL=http://localhost:11434
NEXT_PUBLIC_OBSIDIAN_URL=https://192.168.50.43:27124
```

### Settings Panel
The settings panel allows you to configure:
- **API URLs**: Backend and external service endpoints
- **Model Parameters**: Temperature, max tokens, top-k values
- **Feature Toggles**: Enable/disable RAG, Obsidian, Web search
- **UI Preferences**: Theme, layout, and display options

## 🎯 Usage

### Starting a Conversation
1. **Select Mode**: Choose between Obsidian, RAG, or Spec generation
2. **Type Message**: Enter your question or request
3. **Send**: Press Enter or click the send button
4. **View Response**: See the AI response with source citations

### Managing Chats
- **New Chat**: Click "New Chat" to start a fresh conversation
- **Chat History**: Browse previous conversations in the sidebar
- **Delete Chats**: Remove unwanted conversations
- **Search**: Find specific messages or topics

### Configuring Models
1. **Open Settings**: Click the gear icon in the header
2. **Select Model**: Choose from available Ollama models
3. **Adjust Parameters**: Fine-tune temperature and token limits
4. **Save**: Apply changes immediately

### Using Features
- **Obsidian Mode**: Access your personal trading notes
- **RAG Mode**: Search the document knowledge base
- **Web Search**: Get real-time market information
- **Spec Generation**: Create structured trading strategies

## 🔒 Security

### Authentication
- Secure session management
- Token-based authentication
- Automatic session refresh

### Data Privacy
- All data stays local (no external API calls for core features)
- Optional web search can be disabled
- Personal notes remain private

### Network Security
- HTTPS support for external APIs
- CORS configuration for secure cross-origin requests
- Input validation and sanitization

## 🚀 Deployment

### Docker Deployment
```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f frontend

# Stop services
docker compose down
```

### Manual Deployment
```bash
# Build the application
npm run build

# Start production server
npm start
```

## 🛠️ Development

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Code Style
- TypeScript strict mode enabled
- ESLint configuration for code quality
- Prettier for consistent formatting
- Component-based architecture

## 📱 Mobile Support

The frontend is fully responsive and works great on:
- **Desktop**: Full feature set with sidebar
- **Tablet**: Optimized layout with collapsible sidebar
- **Mobile**: Touch-friendly interface with bottom navigation

## 🎨 Theming

### Theme System
- **Light Theme**: Clean, professional appearance
- **Dark Theme**: Easy on the eyes for extended use
- **System Theme**: Automatically follows OS preference
- **Custom Colors**: Extensible color system

### Customization
- Modify `tailwind.config.js` for color schemes
- Update component styles in `globals.css`
- Add new themes in the settings panel

## 🔧 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if RAG backend is running on port 8001
   - Verify API URL in settings
   - Check network connectivity

2. **Models Not Loading**
   - Ensure Ollama is running and accessible
   - Check model availability
   - Verify API permissions

3. **Obsidian Integration Not Working**
   - Confirm Obsidian Local REST API is enabled
   - Check API key and URL configuration
   - Verify vault path is correct

### Debug Mode
Enable debug logging by setting:
```bash
NODE_ENV=development
```

## 📈 Performance

### Optimization Features
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js built-in optimization
- **Caching**: Aggressive caching for API responses
- **Lazy Loading**: Components loaded on demand

### Monitoring
- Real-time performance metrics
- Error tracking and reporting
- Usage analytics (optional)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- Follow TypeScript best practices
- Use meaningful component names
- Add proper error handling
- Include JSDoc comments

## 📄 License

This project is part of the EminiPlayer RAG system. See the main project license for details.

---

**Ready to build your trading strategy assistant?** 🚀

The frontend provides a powerful, user-friendly interface for interacting with your RAG system. Whether you're researching trading strategies, analyzing market data, or building automated systems, this interface makes it all accessible and intuitive.