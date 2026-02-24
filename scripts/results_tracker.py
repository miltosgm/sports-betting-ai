#!/usr/bin/env python3
"""
Results Tracker — fetches finished match scores, updates predictions JSON,
posts results to Telegram channel.
"""

import asyncio
import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from telegram import Bot

BASE_DIR = Path(__file__).resolve().parent.parent
PREDICTIONS_DIR = BASE_DIR / 'data' / 'predictions'
RESULTS_DIR = BASE_DIR / 'data' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '')
HEADERS = {'X-Auth-Token': API_KEY}
BASE_URL = 'https://api.football-data.org/v4'

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

FREE_BOT_TOKEN = os.getenv('FREE_BOT_TOKEN')
FREE_CHANNEL_ID = os.getenv('FREE_CHANNEL_ID')

TEAM_NORMALIZE = {
    'Wolverhampton Wanderers FC': 'Wolverhampton Wanderers',
    'Arsenal FC': 'Arsenal',
    'Aston Villa FC': 'Aston Villa',
    'Leeds United FC': 'Leeds United',
    'Brentford FC': 'Brentford',
    'Brighton & Hove Albion FC': 'Brighton & Hove Albion',
    'Chelsea FC': 'Chelsea',
    'Burnley FC': 'Burnley',
    'West Ham United FC': 'West Ham United',
    'AFC Bournemouth': 'Bournemouth',
    'Manchester City FC': 'Manchester City',
    'Newcastle United FC': 'Newcastle United',
    'Sunderland AFC': 'Sunderland',
    'Fulham FC': 'Fulham',
    'Crystal Palace FC': 'Crystal Palace',
    'Nottingham Forest FC': 'Nottingham Forest',
    'Liverpool FC': 'Liverpool',
    'Tottenham Hotspur FC': 'Tottenham Hotspur',
    'Everton FC': 'Everton',
    'Manchester United FC': 'Manchester United',
}


def normalize(name):
    return TEAM_NORMALIZE.get(name, name.replace(' FC', '').replace(' AFC', '').strip())


def fetch_finished_matches(days_back=2):
    """Fetch recently finished PL matches"""
    date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    date_to = datetime.now().strftime('%Y-%m-%d')
    try:
        r = requests.get(
            f"{BASE_URL}/competitions/PL/matches",
            headers=HEADERS,
            params={'status': 'FINISHED', 'dateFrom': date_from, 'dateTo': date_to},
            timeout=10
        )
        if r.status_code == 200:
            results = {}
            for m in r.json().get('matches', []):
                home = normalize(m['homeTeam']['name'])
                away = normalize(m['awayTeam']['name'])
                hg = m['score']['fullTime']['home']
                ag = m['score']['fullTime']['away']
                key = f"{home}-{away}"
                results[key] = {
                    'home_goals': hg,
                    'away_goals': ag,
                    'result': 'Home Win' if hg > ag else ('Away Win' if ag > hg else 'Draw'),
                    'score': f"{hg}-{ag}"
                }
            print(f"✅ Fetched {len(results)} finished matches")
            return results
        else:
            print(f"⚠️ API returned {r.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}


def load_predictions():
    """Load the most recent predictions file"""
    files = sorted(PREDICTIONS_DIR.glob('picks_*.json'), reverse=True)
    if not files:
        print("⚠️ No predictions files found")
        return None, None
    latest = files[0]
    with open(latest) as f:
        data = json.load(f)
    print(f"✅ Loaded predictions: {latest.name}")
    return data, latest


def update_results(predictions, finished):
    """Match predictions to finished results"""
    updated = []
    for pick in predictions:
        home = normalize(pick['home'])
        away = normalize(pick['away'])
        key = f"{home}-{away}"

        result = finished.get(key)
        if result:
            actual = result['result']
            predicted = pick['prediction']
            correct = actual == predicted
            pick['result'] = actual
            pick['score'] = result['score']
            pick['correct'] = correct
            pick['settled'] = True
        else:
            pick.setdefault('settled', False)
        updated.append(pick)
    return updated


def build_results_message(predictions):
    """Build Telegram results message"""
    settled = [p for p in predictions if p.get('settled')]
    if not settled:
        return None

    wins = sum(1 for p in settled if p.get('correct'))
    losses = len(settled) - wins
    profit = sum(
        (p['odds'] - 1) if p.get('correct') else -1
        for p in settled
    )

    lines = []
    lines.append("📊 <b>KICK LAB AI — RESULTS UPDATE</b>")
    lines.append("")

    for p in settled:
        home_s = normalize(p['home'])
        away_s = normalize(p['away'])
        icon = "✅" if p.get('correct') else "❌"
        lines.append(f"{icon} <b>{home_s} vs {away_s}</b>")
        lines.append(f"   Score: {p.get('score', '?')} | Result: {p.get('result', '?')}")
        lines.append(f"   Our Pick: {p['prediction']} @ {p['odds']:.2f} {'✅' if p.get('correct') else '❌'}")
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📈 This batch: <b>{wins}W - {losses}L</b> | P/L: <b>{profit:+.2f}u</b>")
    lines.append("⚡ @kicklabai_bot | #PremierLeague")
    return "\n".join(lines)


async def post_results(message):
    bot = Bot(token=BOT_TOKEN)
    r = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode='HTML',
        disable_web_page_preview=True,
    )
    print(f"✅ Results posted! ID: {r.message_id}")


def build_free_win_message(wins_list):
    """Build win announcement for the free channel (wins only)"""
    lines = ["🏆 <b>KICK LAB AI — WIN ALERT</b> 🏆", ""]
    for p in wins_list:
        home_s = normalize(p['home'])
        away_s = normalize(p['away'])
        lines.append(f"✅ <b>{home_s} vs {away_s}</b>")
        lines.append(f"   Score: {p.get('score', '?')} | Pick: {p['prediction']} @ {p['odds']:.2f}")
        lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append("⚡ We called it. Follow for daily picks.")
    lines.append("👉 @kicklabai_bot | kicklabai.com")
    return "\n".join(lines)


async def post_free_wins(wins_list):
    """Post wins to the free channel"""
    if not FREE_BOT_TOKEN or not FREE_CHANNEL_ID:
        print("⚠️ Free channel credentials missing, skipping")
        return
    message = build_free_win_message(wins_list)
    bot = Bot(token=FREE_BOT_TOKEN)
    r = await bot.send_message(
        chat_id=FREE_CHANNEL_ID,
        text=message,
        parse_mode='HTML',
        disable_web_page_preview=True,
    )
    print(f"✅ Win posted to free channel! ID: {r.message_id}")


def main():
    print("=" * 50)
    print("📊 KICK LAB AI — RESULTS TRACKER")
    print("=" * 50)

    # Fetch finished matches
    finished = fetch_finished_matches(days_back=3)
    if not finished:
        print("No finished matches found yet.")
        return

    # Load predictions
    predictions, pred_file = load_predictions()
    if not predictions:
        return

    # Update with results
    updated = update_results(predictions, finished)

    # Save updated predictions
    with open(pred_file, 'w') as f:
        json.dump(updated, f, indent=2)
    print(f"✅ Updated predictions saved")

    # Show summary
    settled = [p for p in updated if p.get('settled')]
    if settled:
        wins = sum(1 for p in settled if p.get('correct'))
        print(f"\n📊 Results: {wins}/{len(settled)} correct")
        for p in settled:
            icon = "✅" if p.get('correct') else "❌"
            print(f"  {icon} {normalize(p['home'])} vs {normalize(p['away'])}: {p.get('score')} (predicted {p['prediction']})")

        # Post to main channel
        msg = build_results_message(updated)
        if msg:
            asyncio.run(post_results(msg))

        # Post wins to free channel
        wins_list = [p for p in settled if p.get('correct')]
        if wins_list:
            asyncio.run(post_free_wins(wins_list))
        else:
            print("No wins to post to free channel")
    else:
        print("No settled predictions yet (matches may not have been played)")


if __name__ == '__main__':
    main()
