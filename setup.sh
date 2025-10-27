#!/bin/bash

echo "Gemini OSS Agent Integration Setup"

# Check Python version
echo -e "\nChecking Python version..."
python3 --version

# Create virtual environment
echo -e "\nCreating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo -e "\nActivating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo -e "\nUpgrading pip..."
pip install --upgrade pip

# Install requirements
echo -e "\nInstalling requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\nCreating .env file from template..."
    cp .env.example .env
    echo "Please edit .env and add your GOOGLE_API_KEY"
else
    echo -e "\n.env file already exists"
fi


echo "Setup complete!"
echo -e "\nNext steps:"
echo "1. Edit .env and add your GOOGLE_API_KEY"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Test your setup: python test_gemini_setup.py"
