#!/usr/bin/env python3
"""
Real-Time Results Tracker — runs every 5 minutes during match windows.
Checks for newly finished PL matches, posts results immediately to Telegram,
and only posts each result once (state tracked in data/results/posted_state.json).
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

STATE_FILE = RESULTS_DIR / 'posted_state.json'

API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '')
HEADERS = {'X-Auth-Token': API_KEY}
BASE_URL = 'https://api.football-data.org/v4'

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

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


def load_state():
    """Load set of already-posted match keys"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            data = json.load(f)
        return set(data.get('posted', []))
    return set()


def save_state(posted_keys: set):
    """Persist posted match keys"""
    with open(STATE_FILE, 'w') as f:
        json.dump({'posted': list(posted_keys), 'updated': datetime.utcnow().isoformat()}, f, indent=2)


def fetch_finished_matches(days_back=3):
    """Fetch recently finished PL matches from football-data.org"""
    date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    date_to = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
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
                if hg is None or ag is None:
                    continue
                key = f"{home}-{away}"
                results[key] = {
                    'home_goals': hg,
                    'away_goals': ag,
                    'result': 'Home Win' if hg > ag else ('Away Win' if ag > hg else 'Draw'),
                    'score': f"{hg}-{ag}",
                    'home': home,
                    'away': away,
                }
            print(f"✅ Fetched {len(results)} finished matches")
            return results
        else:
            print(f"⚠️ API returned {r.status_code}: {r.text[:200]}")
            return {}
    except Exception as e:
        print(f"❌ Error fetching matches: {e}")
        return {}


def load_predictions():
    """Load most recent predictions JSON"""
    files = sorted(PREDICTIONS_DIR.glob('picks_*.json'), reverse=True)
    if not files:
        print("⚠️ No predictions files found")
        return None, None
    latest = files[0]
    with open(latest) as f:
        data = json.load(f)
    print(f"✅ Loaded predictions: {latest.name} ({len(data)} picks)")
    return data, latest


def build_result_message(pick, result_data, correct):
    """Build a single-pick result Telegram message"""
    home_s = normalize(pick['home'])
    away_s = normalize(pick['away'])
    score = result_data['score']
    actual = result_data['result']
    predicted = pick['prediction']
    odds = pick.get('odds', 0)
    edge = pick.get('edge', 0)

    if correct:
        profit = odds - 1
        icon = "✅"
        verdict = f"WIN +{profit:.2f}u"
        color_tag = "🟢"
    else:
        icon = "❌"
        verdict = "LOSS -1.00u"
        color_tag = "🔴"

    lines = [
        f"{icon} <b>RESULT: {home_s} vs {away_s}</b>",
        f"",
        f"⚽ Final Score: <b>{score}</b>",
        f"🎯 Our Pick: <b>{predicted} @ {odds:.2f}</b>",
        f"📊 Actual: <b>{actual}</b>",
        f"",
        f"{color_tag} <b>{verdict}</b>",
    ]

    if edge and edge > 0:
        lines.append(f"📈 Edge was: +{edge:.1f}%")

    lines.append("")
    lines.append("⚡ <a href='https://kicklabai.com/results_verified.html'>View all results →</a>")
    lines.append("#PremierLeague #KickLabAI")

    return "\n".join(lines)


async def post_message(text):
    bot = Bot(token=BOT_TOKEN)
    r = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        parse_mode='HTML',
        disable_web_page_preview=True,
    )
    print(f"✅ Posted message ID: {r.message_id}")
    return r.message_id


def update_predictions_file(predictions, finished, pred_file):
    """Update predictions JSON with settled results and save"""
    updated = []
    for pick in predictions:
        home = normalize(pick['home'])
        away = normalize(pick['away'])
        key = f"{home}-{away}"
        result = finished.get(key)
        if result and not pick.get('settled'):
            pick['result'] = result['result']
            pick['score'] = result['score']
            pick['correct'] = result['result'] == pick['prediction']
            pick['settled'] = True
        updated.append(pick)

    with open(pred_file, 'w') as f:
        json.dump(updated, f, indent=2)

    # Also copy to docs/data for GitHub Pages
    docs_pred = BASE_DIR / 'docs' / 'data' / 'predictions' / pred_file.name
    docs_pred.parent.mkdir(parents=True, exist_ok=True)
    with open(docs_pred, 'w') as f:
        json.dump(updated, f, indent=2)

    # Update latest.json
    latest_src = BASE_DIR / 'data' / 'predictions' / 'latest.json'
    latest_dst = BASE_DIR / 'docs' / 'data' / 'predictions' / 'latest.json'
    with open(latest_src, 'w') as f:
        json.dump(updated, f, indent=2)
    with open(latest_dst, 'w') as f:
        json.dump(updated, f, indent=2)

    print(f"✅ Updated {pred_file.name} and docs/data copies")
    return updated


def main():
    print("=" * 55)
    print(f"⏱️  KICK LAB AI — REAL-TIME RESULTS TRACKER")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 55)

    # Load already-posted state
    posted_keys = load_state()
    print(f"📋 Already posted: {len(posted_keys)} results")

    # Fetch finished matches from API
    finished = fetch_finished_matches(days_back=3)
    if not finished:
        print("No finished matches found.")
        return

    # Load our predictions
    predictions, pred_file = load_predictions()
    if not predictions:
        return

    # Find newly settled matches (finished AND in our predictions AND not yet posted)
    new_results = []
    for pick in predictions:
        if pick.get('settled'):
            continue  # already processed in file
        home = normalize(pick['home'])
        away = normalize(pick['away'])
        key = f"{home}-{away}"

        if key in finished and key not in posted_keys:
            result_data = finished[key]
            correct = result_data['result'] == pick['prediction']
            new_results.append((pick, result_data, correct, key))

    if not new_results:
        print("✓ No new results to post.")
        return

    print(f"\n🆕 {len(new_results)} new result(s) found!")

    # Update predictions file with all finished matches (not just new ones)
    updated = update_predictions_file(predictions, finished, pred_file)

    # Post each new result to Telegram
    for pick, result_data, correct, key in new_results:
        icon = "✅" if correct else "❌"
        home_s = normalize(pick['home'])
        away_s = normalize(pick['away'])
        print(f"  {icon} {home_s} vs {away_s}: {result_data['score']} (predicted {pick['prediction']})")

        msg = build_result_message(pick, result_data, correct)
        try:
            asyncio.run(post_message(msg))
            posted_keys.add(key)
        except Exception as e:
            print(f"  ⚠️ Failed to post: {e}")

    # Save updated state
    save_state(posted_keys)

    # Summary log
    settled_all = [p for p in updated if p.get('settled')]
    wins_all = sum(1 for p in settled_all if p.get('correct'))
    print(f"\n📊 Session total: {wins_all}/{len(settled_all)} correct")


if __name__ == '__main__':
    main()
