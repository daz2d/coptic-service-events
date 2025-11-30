#!/bin/bash

# Setup script for Coptic Service Events Bot

echo "========================================"
echo "Coptic Service Events Bot - Setup"
echo "========================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""

# Install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file (please configure it)"
else
    echo "✓ .env file already exists"
fi
echo ""

# Check config
echo "Configuration checklist:"
echo "  [ ] Edit config.json to set your location (ZIP code or use current location)"
echo "  [ ] Add church/diocese websites to config.json data_sources"
echo "  [ ] (Optional) Set up Google Calendar API:"
echo "      - See docs/google_calendar_setup.md for instructions"
echo "      - Place credentials.json in project root"
echo "  [ ] (Optional) Configure email notifications in .env"
echo ""

echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Try the demo: python quickstart.py"
echo "  3. Configure your settings in config.json"
echo "  4. Run the bot: python main.py --once"
echo ""
