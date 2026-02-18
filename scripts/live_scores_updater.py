#!/usr/bin/env python3
"""
Fetches live PL scores every 2 minutes and writes to data/live_scores.json
Dashboard reads this static file — no CORS issues.
"""
import json, requests, os, subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT = BASE_DIR / 'data' / 'live_scores.json'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '187d23f874344449b4544acdee9e0fb7')
HEADERS = {'X-Auth-Token': API_KEY}

def fetch():
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    r = requests.get(
        f'https://api.football-data.org/v4/competitions/PL/matches',
        headers=HEADERS,
        params={'dateFrom': today, 'dateTo': today},
        timeout=10
    )
    r.raise_for_status()
    matches = []
    for m in r.json().get('matches', []):
        ht = m['score']['fullTime']['home']
        at = m['score']['fullTime']['away']
        if ht is None:
            ht = m['score']['halfTime']['home']
            at = m['score']['halfTime']['away']
        matches.append({
            'home': m['homeTeam']['name'],
            'away': m['awayTeam']['name'],
            'homeShort': m['homeTeam'].get('shortName', m['homeTeam']['name']),
            'awayShort': m['awayTeam'].get('shortName', m['awayTeam']['name']),
            'status': m['status'],   # SCHEDULED, IN_PLAY, PAUSED, FINISHED, TIMED
            'minute': m.get('minute'),
            'homeGoals': ht,
            'awayGoals': at,
        })
    return matches

def main():
    try:
        matches = fetch()
        out = {
            'updatedAt': datetime.now(timezone.utc).isoformat(),
            'updatedAtAthens': datetime.now().strftime('%H:%M'),
            'matches': matches
        }
        with open(OUTPUT, 'w') as f:
            json.dump(out, f, indent=2)
        
        # Push to GitHub
        subprocess.run(['git', 'add', str(OUTPUT)], cwd=BASE_DIR)
        result = subprocess.run(
            ['git', 'commit', '-m', f'Live scores update {out["updatedAtAthens"]}'],
            cwd=BASE_DIR, capture_output=True, text=True
        )
        if 'nothing to commit' not in result.stdout + result.stderr:
            subprocess.run(['git', 'push'], cwd=BASE_DIR)
            print(f'✅ Pushed live scores at {out["updatedAtAthens"]}')
        else:
            print(f'ℹ️  No changes at {out["updatedAtAthens"]}')
        
        # Print summary
        for m in matches:
            if m['status'] in ('IN_PLAY', 'PAUSED', 'FINISHED'):
                print(f"  {m['status']}: {m['homeShort']} {m['homeGoals']}-{m['awayGoals']} {m['awayShort']}")
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    main()
