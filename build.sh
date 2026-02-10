#!/bin/bash
# Build script for Hardsubber macOS app

echo "Building Hardsubber.app..."
echo "================================"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install pyinstaller if not installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the app
echo "Building application..."
pyinstaller --clean hardsubber.spec

# Check if build was successful
if [ -d "dist/Hardsubber.app" ]; then
    echo ""
    echo "================================"
    echo "✓ Build successful!"
    echo "================================"
    echo ""
    echo "Your app is ready at: dist/Hardsubber.app"
    echo ""
    echo "To install:"
    echo "  cp -r dist/Hardsubber.app /Applications/"
    echo ""
    echo "To run:"
    echo "  open dist/Hardsubber.app"
    echo ""
else
    echo ""
    echo "================================"
    echo "✗ Build failed!"
    echo "================================"
    exit 1
fi
