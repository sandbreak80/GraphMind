#!/bin/bash

# Script to push EminiPlayer to new GraphMind GitHub repository
# Created: October 25, 2025

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║        🚀 PUSHING TO GITHUB: GraphMind 🚀                           ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Configuration
REPO_URL="https://github.com/sandbreak80/GraphMind.git"
REMOTE_NAME="graphmind"

echo "📋 Repository Details:"
echo "  • Remote Name: $REMOTE_NAME"
echo "  • Repository URL: $REPO_URL"
echo "  • Branch: main"
echo ""

# Check if remote already exists
if git remote | grep -q "^${REMOTE_NAME}$"; then
    echo "ℹ️  Remote '$REMOTE_NAME' already exists. Updating URL..."
    git remote set-url $REMOTE_NAME $REPO_URL
else
    echo "➕ Adding new remote '$REMOTE_NAME'..."
    git remote add $REMOTE_NAME $REPO_URL
fi

echo "✅ Remote configured"
echo ""

# Verify remote
echo "📡 Verifying remote..."
git remote -v | grep $REMOTE_NAME
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"
echo ""

# Count commits
COMMIT_COUNT=$(git rev-list --count HEAD)
echo "📊 Total commits to push: $COMMIT_COUNT"
echo ""

# Show recent commits
echo "📝 Recent commits (last 5):"
git log --oneline -5
echo ""

# Confirm before pushing
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANT: Make sure you've created the repository on GitHub first!"
echo ""
echo "   Go to: https://github.com/new"
echo "   Repository name: GraphMind"
echo "   Visibility: Public (recommended) or Private"
echo "   Do NOT initialize with README, .gitignore, or license"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Have you created the GitHub repository? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo ""
    echo "❌ Push cancelled. Create the repository first, then run this script again."
    echo ""
    echo "Quick steps:"
    echo "  1. Go to https://github.com/new"
    echo "  2. Name: GraphMind"
    echo "  3. Click 'Create repository'"
    echo "  4. Run this script again"
    exit 0
fi

echo ""
echo "🚀 Pushing to GitHub..."
echo ""

# Push main branch
echo "📤 Pushing main branch..."
if git push $REMOTE_NAME main; then
    echo "✅ Main branch pushed successfully"
else
    echo "⚠️  Push failed. This might be because:"
    echo "   • The repository doesn't exist yet"
    echo "   • You don't have permission"
    echo "   • Authentication failed"
    echo ""
    echo "Try:"
    echo "   git push $REMOTE_NAME main --verbose"
    exit 1
fi

echo ""

# Push tags if any
TAG_COUNT=$(git tag | wc -l)
if [ $TAG_COUNT -gt 0 ]; then
    echo "🏷️  Pushing $TAG_COUNT tags..."
    git push $REMOTE_NAME --tags
    echo "✅ Tags pushed successfully"
else
    echo "ℹ️  No tags to push"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║        ✅ SUCCESSFULLY PUSHED TO GITHUB! ✅                          ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Push Summary:"
echo "  • Commits pushed: $COMMIT_COUNT"
echo "  • Branch: main"
echo "  • Tags: $TAG_COUNT"
echo "  • Remote: $REMOTE_NAME"
echo ""
echo "🌐 View your repository:"
echo "  https://github.com/sandbreak80/GraphMind"
echo ""
echo "📋 Next Steps:"
echo "  1. Visit your repository on GitHub"
echo "  2. Add repository description"
echo "  3. Add topics: rag, ai, llm, ollama, nextjs, fastapi"
echo "  4. Set up GitHub Pages (optional)"
echo "  5. Enable Issues and Discussions"
echo "  6. Add collaborators (if needed)"
echo ""
echo "🎉 GraphMind is now on GitHub!"
echo ""

