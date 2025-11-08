#!/bin/bash
# Setup script for poker.ev

echo "================================"
echo "poker.ev Setup Script"
echo "================================"
echo

# Check Python version
echo "Checking Python version..."
python3 --version

echo
echo "Installing dependencies..."
echo

# Install main dependencies
echo "Installing pygame, numpy, and testing tools..."
pip3 install pygame numpy pytest pytest-cov black mypy

echo
echo "Installing texasholdem dependencies..."
pip3 install Deprecated

echo
echo "Installing texasholdem from local directory..."
cd texasholdem
pip3 install -e .
cd ..

echo
echo "================================"
echo "Setup complete!"
echo "================================"
echo
echo "To run poker.ev:"
echo "  python3 main.py"
echo
echo "To run a simple example:"
echo "  python3 examples/simple_game.py"
echo
