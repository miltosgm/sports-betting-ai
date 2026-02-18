#!/bin/bash
# Evening results check + post to Telegram
PROJ="/Users/milton/sports-betting-ai"
cd "$PROJ"
echo "=== $(date) - Running results tracker ==="
python3 scripts/results_tracker.py
git add -A
git commit -m "Auto: results update $(date +%Y-%m-%d)" || echo "Nothing to commit"
git push
echo "=== Done ==="
