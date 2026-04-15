#!/bin/bash
# Build script for Render deployment
# This script installs dependencies in a way that avoids Rust compilation issues

set -e

echo "🔄 Updating pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "🔄 Installing requirements with binary-only preference..."
# First try: Install with no build isolation (avoids Rust compilation)
pip install --no-cache-dir \
    --no-build-isolation \
    --prefer-binary \
    --no-deps \
    -r backend/requirements.txt || true

# Second try: Fallback to basic install if first fails
echo "🔄 Installing with fallback method..."
pip install --no-cache-dir \
    --prefer-binary \
    -r backend/requirements.txt

echo "✅ Dependencies installed successfully!"
echo "📦 Installed packages:"
pip list
