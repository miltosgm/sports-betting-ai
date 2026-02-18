#!/usr/bin/env python3
"""Send individual pick messages in the clean card format."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from telegram import Bot

CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Real bet365 decimal odds — Feb 18, 2026
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


def format_pick(p):
    return (
        f"⚽ {p['home']} vs {p['away']}\n"
        f"🕐 {p['time']} GMT+2 | Premier League\n"
        f"\n"
        f"🎯 Prediction: <b>{p['prediction']}</b>\n"
        f"📊 Confidence: <b>{p['confidence']}%</b>\n"
        f"💰 Odds: <b>{p['odds']:.2f}</b>\n"
        f"📈 Edge: <b>+{p['edge']}%</b>"
    )


async def send():
    bot = Bot(token=BOT_TOKEN)
    
    # Header message
    header = (
        "⚡ <b>KICK LAB AI — MATCHWEEK 26 PICKS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📅 Wed 18 — Mon 23 Feb 2026\n"
        "🎯 5 Value Picks | Real Odds\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=header,
        parse_mode='HTML',
    )
    print("✅ Header sent")
    await asyncio.sleep(1)
    
    # Individual picks
    for i, pick in enumerate(PICKS):
        msg = format_pick(pick)
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=msg,
            parse_mode='HTML',
        )
        print(f"✅ Pick {i+1} sent: {pick['home']} vs {pick['away']}")
        await asyncio.sleep(1.5)
    
    print("\n🎉 All picks sent!")


if __name__ == '__main__':
    asyncio.run(send())
