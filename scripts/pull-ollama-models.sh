#!/bin/bash

# GraphMind Ollama Models Auto-Pull Script
# This script automatically pulls all required models for GraphMind

echo "🧠 GraphMind Ollama Models Auto-Pull Starting..."

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "   Waiting for Ollama service..."
    sleep 5
done

echo "✅ Ollama is ready, starting model downloads..."

# Default chat / research
echo "📥 Pulling llama3.1:8b-instruct (default chat/research)..."
ollama pull llama3.1:8b-instruct

# Reasoning / tough analysis
echo "📥 Pulling deepseek-r1:14b (reasoning/tough analysis)..."
ollama pull deepseek-r1:14b

echo "📥 Pulling deepseek-r1:7b (reasoning/tough analysis)..."
ollama pull deepseek-r1:7b

# Long-context / all-in-one deep dives
echo "📥 Pulling qwen2.5:14b (long-context/deep dives)..."
ollama pull qwen2.5:14b

echo "📥 Pulling qwen2.5:32b (long-context/deep dives)..."
ollama pull qwen2.5:32b

# Coding / tool logic
echo "📥 Pulling qwen2.5-coder:7b (coding/tool logic)..."
ollama pull qwen2.5-coder:7b

echo "📥 Pulling qwen2.5-coder:14b (coding/tool logic)..."
ollama pull qwen2.5-coder:14b

# Small model (prompt uplift, planner, classifiers)
echo "📥 Pulling llama3.2:3b-instruct (small model/prompt uplift)..."
ollama pull llama3.2:3b-instruct

echo "📥 Pulling phi3:mini (small model/planner/classifiers)..."
ollama pull phi3:mini

# Vision (optional)
echo "📥 Pulling qwen3-vl (vision model)..."
ollama pull qwen3-vl

echo "🎉 All GraphMind models downloaded successfully!"
echo ""
echo "📋 Available models:"
ollama list
