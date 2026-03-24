#!/bin/bash

# Stock Analysis System - Quick Start Script

echo "============================================================"
echo "        A股自选股智能分析系统 Stock Analysis System"
echo "============================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not detected. Please install first"
    echo "Mac: brew install python@3.10"
    echo "Ubuntu: sudo apt install python3.10"
    exit 1
fi

echo "[OK] Python installed: $(python3 --version)"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "[INFO] .env configuration file not found"
    echo ""
    echo "Creating .env from .env.example..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[OK] .env file created"
        echo ""
        echo "============================================================"
        echo "     Please edit .env file and add your LLM API Key"
        echo "============================================================"
        echo ""
        echo "Recommended options:"
        echo "  1. Google Gemini (Free tier available)"
        echo "     Visit: https://aistudio.google.com/"
        echo ""
        echo "  2. DeepSeek (Cost-effective)"
        echo "     Visit: https://platform.deepseek.com/"
        echo ""
        read -p "Press Enter to edit .env file..."
        ${EDITOR:-nano} .env
    else
        echo "[ERROR] .env.example file not found"
        exit 1
    fi
fi

echo "============================================================"
echo "           Select Launch Mode"
echo "============================================================"
echo ""
echo "  1. Web Interface (Recommended)"
echo "     Start Web service, use in browser"
echo ""
echo "  2. Command Line Mode"
echo "     Analyze stocks configured in .env"
echo ""
echo "  3. Debug Mode"
echo "     View detailed logs for troubleshooting"
echo ""
echo "  4. Market Review Only"
echo "     Only analyze market, skip individual stocks"
echo ""
echo "  5. Exit"
echo ""
read -p "Please select (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Starting Web service..."
        echo "Access: http://localhost:8000"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        echo "Press Ctrl+C to stop service"
        echo ""
        python3 main.py --serve-only --port 8000
        ;;
    2)
        echo ""
        echo "Starting stock analysis..."
        echo ""
        python3 main.py
        ;;
    3)
        echo ""
        echo "Running in debug mode..."
        echo ""
        python3 main.py --debug
        ;;
    4)
        echo ""
        echo "Executing market review..."
        echo ""
        python3 main.py --market-review --no-notify
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid selection, exiting..."
        exit 1
        ;;
esac
