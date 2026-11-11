#!/bin/bash

echo "=============================================="
echo "Communication Scanner - Quick Setup"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo ""
    echo "Please install Ollama from: https://ollama.ai"
    echo ""
    echo "After installing, run:"
    echo "  ollama pull llama3.2"
    echo "  ollama serve"
    exit 1
fi

echo "✓ Ollama found: $(ollama --version)"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama server is not running."
    echo ""
    echo "Starting Ollama server..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 2
    echo "✓ Ollama server started (PID: $OLLAMA_PID)"
else
    echo "✓ Ollama server is running"
fi

echo ""

# Check if llama3.2 model is available
if ollama list | grep -q "llama3.2"; then
    echo "✓ llama3.2 model is installed"
else
    echo "⚠️  llama3.2 model not found."
    echo ""
    echo "Pulling llama3.2 model (this may take a few minutes)..."
    ollama pull llama3.2
    echo "✓ llama3.2 model installed"
fi

echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

echo "✓ Dependencies installed"
echo ""

# Check if config is set up
if [ ! -f "config/config.json" ]; then
    echo "⚠️  Configuration file not found."
    echo "Copying example config..."
    cp config/config.example.json config/config.json
    echo "✓ Config file created at config/config.json"
    echo ""
    echo "⚠️  IMPORTANT: Edit config/config.json with your email credentials"
fi

echo ""
echo "=============================================="
echo "Setup Complete! 🎉"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Edit config/config.json with your email settings"
echo "2. Run: python3 src/scanner.py"
echo ""
echo "For Gmail users:"
echo "  - Use an App Password (not your regular password)"
echo "  - See README.md for instructions"
echo ""
echo "=============================================="
