#!/bin/bash
# Daily picks: run predictions + post to Telegram + push to GitHub
set -e
PROJ="/Users/milton/sports-betting-ai"
cd "$PROJ"
source "$PROJ/.env" 2>/dev/null || true

echo "=== $(date) - Running daily picks ==="
python3 scripts/real_predictions.py
# Always update latest.json so dashboard always loads fresh data
cp data/predictions/picks_$(date +%Y-%m-%d).json data/predictions/latest.json 2>/dev/null || true

python3 - <<'PYEOF'
import asyncio, os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('/Users/milton/sports-betting-ai/.env'))
from telegram import Bot

async def send():
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    msg = open('/Users/milton/sports-betting-ai/data/predictions/latest_telegram_msg.txt').read()
    r = await bot.send_message(
        chat_id=os.getenv('TELEGRAM_CHANNEL_ID'),
        text=msg, parse_mode='HTML', disable_web_page_preview=True
    )
    print(f"✅ Posted picks! ID: {r.message_id}")

asyncio.run(send())
PYEOF

# Push to GitHub
git add -A
git commit -m "Auto: daily picks $(date +%Y-%m-%d)" || echo "Nothing to commit"
git push
echo "=== Done ==="
