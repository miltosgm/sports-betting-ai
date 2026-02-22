#!/usr/bin/env python3
"""
generate_results_json.py
Converts real prediction JSON files into docs/data/results.json
so results_verified.html can load live, real data.

Run after each gameweek settles, or via cron.
"""

import json
import os
import glob
from datetime import datetime

PICKS_DIR   = os.path.join(os.path.dirname(__file__), '..', 'docs', 'data', 'predictions')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'docs', 'data', 'results.json')

def parse_date_str(date_str):
    """Convert 'Sat 21 Feb' or '2026-02-21' to ISO date string."""
    if not date_str:
        return None
    # Already ISO format
    if len(date_str) == 10 and '-' in date_str:
        return date_str
    # 'Sat 21 Feb' format — add year
    try:
        dt = datetime.strptime(date_str + ' 2026', '%a %d %b %Y')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return None

def pick_to_result(pick, file_date):
    """Convert a real pick dict to the results page format."""
    if not pick.get('settled'):
        return None
    if pick.get('correct') is None:
        return None

    home = pick.get('home_short') or pick.get('home', '').replace(' FC', '').strip()
    away = pick.get('away_short') or pick.get('away', '').replace(' FC', '').strip()
    match_str = f"{home} vs {away}"

    # Date: try 'date' field first (may be 'Sat 21 Feb' or '2026-02-21')
    raw_date = pick.get('date', '')
    iso_date = parse_date_str(raw_date) or file_date

    odds    = float(pick.get('odds', 0))
    correct = pick.get('correct', False)
    profit  = round((odds - 1) * 100) if correct else -100
    result  = 'win' if correct else 'loss'

    score = pick.get('score', '')
    edge  = pick.get('edge', 0)

    return {
        'date':       iso_date,
        'time':       pick.get('time', '15:00'),
        'match':      match_str,
        'prediction': pick.get('prediction', ''),
        'odds':       round(odds, 2),
        'confidence': round(float(pick.get('confidence', 0)), 1),
        'edge':       round(float(edge), 1),
        'result':     result,
        'profit':     profit,
        'score':      score,
        'correct':    correct,
        'source':     'real',  # flag so frontend knows this is verified
        'published':  f"{iso_date}T09:00:00+02:00",
    }


def main():
    results = []
    seen    = set()  # dedup key: match + date

    # Find all picks_YYYY-MM-DD.json files
    pattern = os.path.join(PICKS_DIR, 'picks_*.json')
    files   = sorted(glob.glob(pattern))
    print(f"Found {len(files)} pick files")

    for filepath in files:
        filename  = os.path.basename(filepath)
        file_date = filename.replace('picks_', '').replace('.json', '')  # e.g. 2026-02-21

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  ⚠️  Error reading {filename}: {e}")
            continue

        picks = data if isinstance(data, list) else data.get('picks', [])
        file_results = 0

        for pick in picks:
            r = pick_to_result(pick, file_date)
            if r is None:
                continue

            dedup_key = f"{r['match']}|{r['date']}"
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            results.append(r)
            file_results += 1

        print(f"  {filename}: {len(picks)} picks → {file_results} settled results")

    # Sort newest first
    results.sort(key=lambda x: x['date'], reverse=True)

    # Summary stats
    wins   = sum(1 for r in results if r['result'] == 'win')
    losses = sum(1 for r in results if r['result'] == 'loss')
    total  = wins + losses
    profit = sum(r['profit'] for r in results)

    output = {
        'generated':   datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'count':       len(results),
        'wins':        wins,
        'losses':      losses,
        'win_rate':    round(wins / total * 100, 1) if total > 0 else 0,
        'total_profit': profit,
        'results':     results,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ {len(results)} real results → {OUTPUT_FILE}")
    print(f"   {wins}W - {losses}L ({output['win_rate']}% win rate)")
    print(f"   Total profit: €{profit:+}")


if __name__ == '__main__':
    main()
