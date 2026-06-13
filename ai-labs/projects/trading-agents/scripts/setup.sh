#!/bin/bash
# Setup script for Trading Agents

set -e

echo "================================"
echo "Trading Agents - Setup"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "================================"
echo "✓ Setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Activate venv: source venv/bin/activate"
echo "2. Copy .env.example to .env and fill in API keys"
echo "3. Run tests: python scripts/test_data_fetchers.py"
echo ""
