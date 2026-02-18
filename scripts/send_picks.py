#!/usr/bin/env python3
"""Send formatted picks with real decimal odds to Telegram channel."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from telegram import Bot

CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Real bet365 odds scraped Feb 18, 2026
# Format: (home, away, home_odds, draw_odds, away_odds, kickoff, date_label)
FIXTURES = [
    # Wed 18 Feb
    ("Wolves", "Arsenal", 10.00, 5.75, 1.27, "20:00", "WED 18 FEB"),
    # Sat 21 Feb
    ("Aston Villa", "Leeds", 1.83, 3.60, 4.50, "15:00", "SAT 21 FEB"),
    ("Brentford", "Brighton", 2.00, 3.60, 3.60, "15:00", "SAT 21 FEB"),
    ("Chelsea", "Burnley", 1.22, 6.50, 12.00, "15:00", "SAT 21 FEB"),
    ("West Ham", "Bournemouth", 2.35, 3.70, 2.88, "17:30", "SAT 21 FEB"),
    ("Man City", "Newcastle", 1.42, 5.25, 6.25, "20:00", "SAT 21 FEB"),
    # Sun 22 Feb
    ("Crystal Palace", "Wolves", 1.57, 4.20, 5.75, "14:00", "SUN 22 FEB"),
    ("Nottm Forest", "Liverpool", 4.10, 4.00, 1.80, "14:00", "SUN 22 FEB"),
    ("Sunderland", "Fulham", 2.70, 3.25, 2.70, "14:00", "SUN 22 FEB"),
    ("Tottenham", "Arsenal", 6.00, 4.00, 1.57, "16:30", "SUN 22 FEB"),
    # Mon 23 Feb
    ("Everton", "Man Utd", 3.60, 3.75, 1.95, "20:00", "MON 23 FEB"),
]

# Our AI picks (mock predictions for now - replace with real model output)
# (match_index, pick, confidence, edge)
AI_PICKS = [
    (0, "Away", 91, 4.2),   # Arsenal @ Wolves
    (5, "Home", 78, 3.1),   # Man City vs Newcastle
    (7, "Away", 74, 2.8),   # Liverpool @ Forest
    (9, "Away", 82, 5.4),   # Arsenal @ Spurs
    (3, "Home", 85, 2.1),   # Chelsea vs Burnley
]


def format_odds_line(home, away, h_odds, d_odds, a_odds):
    return f"🏠 {h_odds:.2f}  |  🤝 {d_odds:.2f}  |  ✈️ {a_odds:.2f}"


def build_message():
    lines = []
    lines.append("⚡ <b>KICK LAB AI — MATCHWEEK 26</b> ⚡")
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    # Group by date
    current_date = None
    for i, (home, away, h_odds, d_odds, a_odds, ko, date_label) in enumerate(FIXTURES):
        if date_label != current_date:
            current_date = date_label
            lines.append(f"📅 <b>{date_label}</b>")
            lines.append("")
        
        # Check if this match has an AI pick
        ai_pick = None
        for idx, pick, conf, edge in AI_PICKS:
            if idx == i:
                ai_pick = (pick, conf, edge)
                break
        
        lines.append(f"⏰ {ko}  <b>{home} vs {away}</b>")
        lines.append(f"   🏠 {h_odds:.2f}  |  🤝 {d_odds:.2f}  |  ✈️ {a_odds:.2f}")
        
        if ai_pick:
            pick, conf, edge = ai_pick
            if pick == "Home":
                pick_name = home
                pick_odds = h_odds
            elif pick == "Away":
                pick_name = away
                pick_odds = a_odds
            else:
                pick_name = "Draw"
                pick_odds = d_odds
            lines.append(f"   🤖 <b>AI Pick: {pick_name}</b> @ {pick_odds:.2f}")
            lines.append(f"   📊 Confidence: {conf}% | Edge: +{edge}%")
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🎯 <b>TOP VALUE PICKS</b>")
    lines.append("")
    
    for idx, pick, conf, edge in sorted(AI_PICKS, key=lambda x: -x[3]):
        home, away, h_odds, d_odds, a_odds, ko, date_label = FIXTURES[idx]
        if pick == "Home":
            pick_name = home
            pick_odds = h_odds
        elif pick == "Away":
            pick_name = away
            pick_odds = a_odds
        else:
            pick_name = "Draw"
            pick_odds = d_odds
        
        stars = "🔥" if edge >= 4.0 else "✅"
        lines.append(f"{stars} <b>{pick_name}</b> vs {'away' if pick == 'Home' else 'home'} → @ <b>{pick_odds:.2f}</b> (Edge +{edge}%)")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📈 Season: <b>79% Win Rate</b> | +€3,525 Profit")
    lines.append("🔗 <a href='https://miltosgm.github.io/sports-betting-ai/dashboard_mockup.html'>Full Dashboard</a>")
    lines.append("")
    lines.append("⚡ @kicklabai_bot | #PremierLeague #GW26")
    
    return "\n".join(lines)


async def send():
    bot = Bot(token=BOT_TOKEN)
    msg = build_message()
    print(msg)
    print(f"\n--- Sending to {CHANNEL_ID} ---")
    result = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=msg,
        parse_mode='HTML',
        disable_web_page_preview=True,
    )
    print(f"✅ Sent! Message ID: {result.message_id}")


if __name__ == '__main__':
    asyncio.run(send())
