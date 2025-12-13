#!/bin/bash

echo "🚀 Starting Facebook Automation Tool..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.7+ first"
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    exit 1
fi

echo
echo "🌟 Starting the application..."
echo "📱 The tool will open in your default browser..."
echo

# Start Streamlit
streamlit run facebook_automation.py --server.port 8501 --server.headless false

echo
echo "👋 Thank you for using Facebook Automation Tool!"