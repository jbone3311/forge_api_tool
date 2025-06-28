#!/bin/bash

# Forge API Tool - Quick Start Ritual
# Run this script at the beginning of each coding session

echo "🎯 Starting Forge API Tool Coding Session..."
echo "=========================================="

# 1. Navigate to project directory
cd "$(dirname "$0")"
echo "📁 Project directory: $(pwd)"

# 2. Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

# 3. Health checks
echo "🔍 Running health checks..."

# Test imports
if ./venv/bin/python tests/unit/test_imports.py >/dev/null 2>&1; then
    echo "✅ Core imports working"
else
    echo "❌ Import issues detected"
fi

# Test API connection
API_STATUS=$(./venv/bin/python -c "from core.forge_api import forge_api_client; print(forge_api_client.test_connection())" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ API connection: $API_STATUS"
else
    echo "❌ API connection failed"
fi

# Check Forge server
if curl -s http://127.0.0.1:7860/sdapi/v1/progress >/dev/null 2>&1; then
    echo "✅ Forge server running"
else
    echo "⚠️  Forge server not running (start with: python web_dashboard/app.py)"
fi

# 4. Project status
echo "📊 Project status:"
git status --porcelain | wc -l | xargs echo "   Uncommitted changes:"
git log --oneline -1 | xargs echo "   Latest commit:"

# 5. Quick test run
echo "🧪 Running quick tests..."
./venv/bin/python run_tests.py --quick 2>/dev/null || echo "   (Quick tests not available)"

echo ""
echo "🎉 Ready to code! Your environment is set up."
echo "💡 Next steps:"
echo "   - Start web dashboard: python web_dashboard/app.py"
echo "   - Run full tests: python run_tests.py"
echo "   - Check logs: tail -f logs/app.log"
echo "" 