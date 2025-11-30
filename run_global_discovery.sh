#!/bin/bash
# Global Church Discovery Runner
# Runs discovery with auto-confirmation and detailed logging

cd /home/minaa/coptic-service-events
source venv/bin/activate

echo "🌍 Starting Global Coptic Orthodox Church Discovery..."
echo "📝 Log file: global_discovery.log"
echo "⏱️  Estimated time: 90-120 minutes"
echo ""

# Auto-answer 'y' to confirmation prompt
echo "y" | python -m src.global_church_discovery 2>&1 | tee global_discovery.log

echo ""
echo "✅ Discovery complete! Check global_discovery.log for details"
