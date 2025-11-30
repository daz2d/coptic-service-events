#!/bin/bash
# Quick progress check for global discovery

echo "🌍 Global Church Discovery - Progress Check"
echo "=========================================="
echo ""

# Check if running
if pgrep -f "global_church_discovery" > /dev/null; then
    echo "✅ Status: RUNNING"
    PID=$(pgrep -f "global_church_discovery")
    echo "📊 Process ID: $PID"
    echo ""
else
    echo "⚠️  Status: NOT RUNNING"
    echo ""
    echo "Start with: ./run_global_discovery.sh &"
    exit 1
fi

# Show latest progress
echo "📈 Latest Progress:"
echo "----------------------------------------"
tail -50 global_discovery.log | grep -E "(✅|⚪|📊|CHECKPOINT|churches in)" | tail -10
echo ""

# Count total churches so far
if [ -f coptic_events.db ]; then
    TOTAL=$(sqlite3 coptic_events.db "SELECT COUNT(*) FROM google_places_churches" 2>/dev/null || echo "0")
    echo "💾 Database: $TOTAL churches saved"
else
    echo "💾 Database: Not yet created"
fi

echo ""
echo "----------------------------------------"
echo "Watch live: tail -f global_discovery.log"
echo "Stop discovery: pkill -f global_church_discovery"
