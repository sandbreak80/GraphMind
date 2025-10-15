#!/bin/bash
# EminiPlayer RAG Service Setup Script

set -e

echo "🚀 EminiPlayer RAG Service Setup"
echo "================================="

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Copy environment template
echo "📋 Creating .env file from template..."
cp .env.template .env

# Set proper permissions
chmod 600 .env

echo "✅ .env file created successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Set DOCUMENTS_DIR to your document collection path"
echo "3. Adjust other settings as needed"
echo "4. Run: docker-compose build"
echo "5. Run: docker-compose up -d"
echo ""
echo "📚 For detailed instructions, see:"
echo "   - SETUP.md (complete setup guide)"
echo "   - SECURITY.md (security best practices)"
echo "   - README.md (quick start)"
echo ""
echo "🎯 Quick test after setup:"
echo "   ./check_status.sh"
