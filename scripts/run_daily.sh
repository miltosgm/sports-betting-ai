#!/bin/bash
#
# Daily Prediction & Results Pipeline for Kick Lab AI
# Run this script every day at 9:00 AM GMT+2 via cron
#
# Cron setup (run `crontab -e`):
# 0 9 * * * /Users/milton/sports-betting-ai/scripts/run_daily.sh >> /Users/milton/sports-betting-ai/logs/cron.log 2>&1
#

set -e  # Exit on error

# Configuration
PROJECT_DIR="/Users/milton/sports-betting-ai"
PYTHON="/usr/bin/env python3"
LOG_DIR="$PROJECT_DIR/logs"
DATE=$(date +"%Y-%m-%d")
TIME=$(date +"%H:%M:%S")

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log file
LOGFILE="$LOG_DIR/daily_run_$DATE.log"

echo "============================================================" | tee -a "$LOGFILE"
echo "🚀 Kick Lab AI - Daily Pipeline" | tee -a "$LOGFILE"
echo "Started: $DATE $TIME" | tee -a "$LOGFILE"
echo "============================================================" | tee -a "$LOGFILE"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Step 1: Generate predictions for upcoming matches
echo "" | tee -a "$LOGFILE"
echo "📊 STEP 1: Generating predictions..." | tee -a "$LOGFILE"
echo "------------------------------------------------------------" | tee -a "$LOGFILE"

if $PYTHON scripts/prediction_pipeline.py >> "$LOGFILE" 2>&1; then
    echo "✅ Predictions generated successfully" | tee -a "$LOGFILE"
else
    echo "❌ Prediction generation failed" | tee -a "$LOGFILE"
    exit 1
fi

# Step 2: Track results from yesterday's games
echo "" | tee -a "$LOGFILE"
echo "📈 STEP 2: Tracking yesterday's results..." | tee -a "$LOGFILE"
echo "------------------------------------------------------------" | tee -a "$LOGFILE"

if $PYTHON scripts/results_tracker.py >> "$LOGFILE" 2>&1; then
    echo "✅ Results tracked successfully" | tee -a "$LOGFILE"
else
    echo "⚠️ Results tracking failed (may be no games yesterday)" | tee -a "$LOGFILE"
    # Don't exit here - results tracking can fail if no games yesterday
fi

# Step 3: Send Telegram notification (optional)
echo "" | tee -a "$LOGFILE"
echo "📱 STEP 3: Sending Telegram notification..." | tee -a "$LOGFILE"
echo "------------------------------------------------------------" | tee -a "$LOGFILE"

# Check if Telegram bot script exists
if [ -f "$PROJECT_DIR/backend/services/telegram_bot.py" ]; then
    # Try to send notification
    if $PYTHON -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
try:
    from backend.services.telegram_bot import send_daily_predictions
    send_daily_predictions()
    print('✅ Telegram notification sent')
except Exception as e:
    print(f'⚠️ Telegram notification failed: {e}')
" >> "$LOGFILE" 2>&1; then
        echo "✅ Telegram notification sent" | tee -a "$LOGFILE"
    else
        echo "⚠️ Telegram notification failed (check bot configuration)" | tee -a "$LOGFILE"
    fi
else
    echo "ℹ️ Telegram bot not configured, skipping notification" | tee -a "$LOGFILE"
fi

# Step 4: Cleanup old predictions (keep last 30 days)
echo "" | tee -a "$LOGFILE"
echo "🗑️ STEP 4: Cleaning up old predictions..." | tee -a "$LOGFILE"
echo "------------------------------------------------------------" | tee -a "$LOGFILE"

# Remove predictions older than 30 days
find "$PROJECT_DIR/data/predictions" -name "*.json" -mtime +30 -delete 2>> "$LOGFILE"
find "$PROJECT_DIR/data/results" -name "*.json" -mtime +30 -delete 2>> "$LOGFILE"
echo "✅ Cleanup complete" | tee -a "$LOGFILE"

# Summary
echo "" | tee -a "$LOGFILE"
echo "============================================================" | tee -a "$LOGFILE"
echo "✅ Daily pipeline completed successfully" | tee -a "$LOGFILE"
echo "Finished: $(date +"%Y-%m-%d %H:%M:%S")" | tee -a "$LOGFILE"
echo "============================================================" | tee -a "$LOGFILE"

# Optional: Send summary to monitoring service
# curl -X POST https://monitoring.example.com/ping -d "kicklab_daily_pipeline_success"

exit 0
