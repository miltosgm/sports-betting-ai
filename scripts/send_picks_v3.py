#!/usr/bin/env python3
"""Send all picks as one single message."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from telegram import Bot

CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

PICKS = [
    {
        "home": "Wolverhampton FC",
        "away": "Arsenal FC",
        "time": "20:00",
        "date": "WED 18 FEB",
        "prediction": "Away Win",
        "confidence": 91,
        "odds": 1.27,
        "edge": 4.2,
    },
    {
        "home": "Chelsea FC",
        "away": "Burnley FC",
        "time": "15:00",
        "date": "SAT 21 FEB",
        "prediction": "Home Win",
        "confidence": 85,
        "odds": 1.22,
        "edge": 2.1,
    },
    {
        "home": "Manchester City",
        "away": "Newcastle United",
        "time": "20:00",
        "date": "SAT 21 FEB",
        "prediction": "Home Win",
        "confidence": 78,
        "odds": 1.42,
        "edge": 3.1,
    },
    {
        "home": "Nottingham Forest",
        "away": "Liverpool FC",
        "time": "14:00",
        "date": "SUN 22 FEB",
        "prediction": "Away Win",
        "confidence": 74,
        "odds": 1.80,
        "edge": 2.8,
    },
    {
        "home": "Tottenham Hotspur FC",
        "away": "Arsenal FC",
        "time": "16:30",
        "date": "SUN 22 FEB",
        "prediction": "Away Win",
        "confidence": 82,
        "odds": 1.57,
        "edge": 5.4,
    },
]


def build_message():
    lines = []
    lines.append("⚡ <b>KICK LAB AI — MATCHWEEK 26</b> ⚡")
    lines.append("")
    
    for p in PICKS:
        lines.append(f"⚽ {p['home']} vs {p['away']}")
        lines.append(f"🕐 {p['time']} GMT+2 | Premier League")
        lines.append("")
        lines.append(f"🎯 Prediction: <b>{p['prediction']}</b>")
        lines.append(f"📊 Confidence: <b>{p['confidence']}%</b>")
        lines.append(f"💰 Odds: <b>{p['odds']:.2f}</b>")
        lines.append(f"📈 Edge: <b>+{p['edge']}%</b>")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
    
    lines.append("📈 Season: <b>79% Win Rate</b> | +€3,525 Profit")
    lines.append("⚡ @kicklabai_bot | #PremierLeague #GW26")
    
    return "\n".join(lines)


async def send():
    bot = Bot(token=BOT_TOKEN)
    msg = build_message()
    result = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=msg,
        parse_mode='HTML',
        disable_web_page_preview=True,
    )
    print(f"✅ Sent! Message ID: {result.message_id}")


if __name__ == '__main__':
    asyncio.run(send())
