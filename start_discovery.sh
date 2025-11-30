#!/bin/bash
# Start discovery in detached mode that survives session disconnects

cd /home/minaa/coptic-service-events
source venv/bin/activate

# Use nohup with proper backgrounding
nohup bash -c "echo y | python -m src.global_church_discovery 2>&1 | tee global_discovery.log" > /dev/null 2>&1 &

PID=$!
echo "✅ Discovery started in detached mode"
echo "📊 Process ID: $PID"
echo "📝 Log file: global_discovery.log"
echo ""
echo "Monitor with: tail -f global_discovery.log"
echo "Check status: ./check_progress.sh"
