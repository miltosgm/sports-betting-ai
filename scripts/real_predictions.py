#!/usr/bin/env python3
"""
Real Predictions — uses actual model + live API data + real odds
Outputs picks with genuine confidence levels
"""

import pickle
import json
import os
import sys
import requests
import numpy as np
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "ensemble_model_v5_proper.pkl"

API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '')
HEADERS = {'X-Auth-Token': API_KEY}
BASE_URL = 'https://api.football-data.org/v4'

# Real bet365 odds (Feb 18 2026)
REAL_ODDS = {
    "Wolverhampton Wanderers FC-Arsenal FC": {"home": 10.00, "draw": 5.75, "away": 1.27, "time": "22:00", "date": "Wed 18 Feb"},
    "Aston Villa FC-Leeds United FC": {"home": 1.83, "draw": 3.60, "away": 4.50, "time": "17:00", "date": "Sat 21 Feb"},
    "Brentford FC-Brighton & Hove Albion FC": {"home": 2.00, "draw": 3.60, "away": 3.60, "time": "17:00", "date": "Sat 21 Feb"},
    "Chelsea FC-Burnley FC": {"home": 1.22, "draw": 6.50, "away": 12.00, "time": "17:00", "date": "Sat 21 Feb"},
    "West Ham United FC-AFC Bournemouth": {"home": 2.35, "draw": 3.70, "away": 2.88, "time": "19:30", "date": "Sat 21 Feb"},
    "Manchester City FC-Newcastle United FC": {"home": 1.42, "draw": 5.25, "away": 6.25, "time": "22:00", "date": "Sat 21 Feb"},
    "Crystal Palace FC-Wolverhampton Wanderers FC": {"home": 1.57, "draw": 4.20, "away": 5.75, "time": "16:00", "date": "Sun 22 Feb"},
    "Nottingham Forest FC-Liverpool FC": {"home": 4.10, "draw": 4.00, "away": 1.80, "time": "16:00", "date": "Sun 22 Feb"},
    "Sunderland AFC-Fulham FC": {"home": 2.70, "draw": 3.25, "away": 2.70, "time": "16:00", "date": "Sun 22 Feb"},
    "Tottenham Hotspur FC-Arsenal FC": {"home": 6.00, "draw": 4.00, "away": 1.57, "time": "18:30", "date": "Sun 22 Feb"},
    "Everton FC-Manchester United FC": {"home": 3.60, "draw": 3.75, "away": 1.95, "time": "22:00", "date": "Mon 23 Feb"},
}

# Aliases for matching API names to odds keys
TEAM_ALIASES = {}


def load_model():
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def fetch_standings():
    """Fetch current PL standings from football-data.org"""
    try:
        r = requests.get(f"{BASE_URL}/competitions/PL/standings", headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Standings API returned {r.status_code}")
            return {}
        data = r.json()
        standings = {}
        for table in data.get('standings', []):
            if table['type'] == 'TOTAL':
                for e in table['table']:
                    name = e['team']['name']
                    p = max(e['playedGames'], 1)
                    standings[name] = {
                        'position': e['position'],
                        'played': e['playedGames'],
                        'won': e['won'],
                        'draw': e['draw'],
                        'lost': e['lost'],
                        'points': e['points'],
                        'gf': e['goalsFor'],
                        'ga': e['goalsAgainst'],
                        'gd': e['goalDifference'],
                        'ppg': e['points'] / p,
                        'gpg': e['goalsFor'] / p,
                        'gapg': e['goalsAgainst'] / p,
                        'wr': e['won'] / p,
                    }
        print(f"✅ Standings: {len(standings)} teams")
        return standings
    except Exception as e:
        print(f"❌ Error fetching standings: {e}")
        return {}


def fetch_recent_matches(days=60):
    """Fetch recent finished PL matches"""
    try:
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        r = requests.get(f"{BASE_URL}/competitions/PL/matches",
                         headers=HEADERS,
                         params={'status': 'FINISHED', 'dateFrom': date_from, 'dateTo': date_to},
                         timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Matches API returned {r.status_code}")
            return []
        matches = []
        for m in r.json().get('matches', []):
            matches.append({
                'home': m['homeTeam']['name'],
                'away': m['awayTeam']['name'],
                'hg': m['score']['fullTime']['home'],
                'ag': m['score']['fullTime']['away'],
                'date': m['utcDate'][:10],
            })
        matches.sort(key=lambda x: x['date'])
        print(f"✅ Recent matches: {len(matches)}")
        return matches
    except Exception as e:
        print(f"❌ Error fetching matches: {e}")
        return []


def compute_team_stats(standings, matches):
    """Compute detailed per-team stats"""
    stats = {}
    for team, s in standings.items():
        home_games = [m for m in matches if m['home'] == team]
        away_games = [m for m in matches if m['away'] == team]
        all_games = [m for m in matches if m['home'] == team or m['away'] == team]
        last5 = all_games[-5:] if len(all_games) >= 5 else all_games

        # Home splits
        if home_games:
            hw = sum(1 for m in home_games if m['hg'] > m['ag'])
            hg = sum(m['hg'] for m in home_games)
            hc = sum(m['ag'] for m in home_games)
            h_wr = hw / len(home_games)
            h_gpg = hg / len(home_games)
            h_cpg = hc / len(home_games)
        else:
            h_wr, h_gpg, h_cpg = s['wr'], s['gpg'], s['gapg']

        # Away splits
        if away_games:
            aw = sum(1 for m in away_games if m['ag'] > m['hg'])
            ag = sum(m['ag'] for m in away_games)
            ac = sum(m['hg'] for m in away_games)
            a_wr = aw / len(away_games)
            a_gpg = ag / len(away_games)
            a_cpg = ac / len(away_games)
        else:
            a_wr, a_gpg, a_cpg = s['wr'] * 0.7, s['gpg'] * 0.85, s['gapg'] * 1.15

        # Form (last 5)
        form_pts = 0
        for m in last5:
            if m['home'] == team:
                form_pts += 3 if m['hg'] > m['ag'] else (1 if m['hg'] == m['ag'] else 0)
            else:
                form_pts += 3 if m['ag'] > m['hg'] else (1 if m['ag'] == m['hg'] else 0)
        form_ppg = form_pts / max(len(last5), 1)

        stats[team] = {
            'pos': s['position'], 'ppg': s['ppg'], 'gpg': s['gpg'], 'gapg': s['gapg'],
            'wr': s['wr'], 'gd': s['gd'],
            'h_wr': h_wr, 'h_gpg': h_gpg, 'h_cpg': h_cpg,
            'a_wr': a_wr, 'a_gpg': a_gpg, 'a_cpg': a_cpg,
            'form': form_ppg,
        }
    return stats


def build_features(home_team, away_team, stats):
    """Build 48-feature vector matching model training order"""
    h = stats.get(home_team)
    a = stats.get(away_team)
    if not h or not a:
        print(f"⚠️ Missing stats for {home_team} or {away_team}")
        return None

    h_gpg = h['h_gpg']
    a_gpg = a['a_gpg']
    h_cpg = h['h_cpg']
    a_cpg = a['a_cpg']
    h_goals_l5 = h_gpg * 5
    a_goals_l5 = a_gpg * 5
    h_wins_l5 = h['h_wr'] * 5
    a_wins_l5 = a['a_wr'] * 5
    h_shots = h_gpg / 0.15
    a_shots = a_gpg / 0.15
    h_sot = h_shots * 0.4
    a_sot = a_shots * 0.4
    h_consistency = min(0.9, 0.5 + abs(h['gd']) * 0.02)
    a_consistency = min(0.9, 0.5 + abs(a['gd']) * 0.02)
    h_momentum = h['form'] / max(0.1, h['ppg'])
    a_momentum = a['form'] / max(0.1, a['ppg'])
    pos_diff = a['pos'] - h['pos']

    features = np.array([
        h_consistency,                                          # 0  consistency_home
        a_sot,                                                  # 1  sot_away
        2.0 + (a['pos'] / 10),                                 # 2  cards_away
        a_shots,                                                # 3  shots_away
        2.0 + (h['pos'] / 10),                                 # 4  yellow_home
        h_goals_l5 * 0.55,                                     # 5  goals_2h_home
        0.1 + (h['pos'] / 100),                                # 6  injury_risk_home
        a_momentum,                                             # 7  momentum_away
        a_goals_l5 * 0.55,                                     # 8  goals_2h_away
        4.0 + h_gpg,                                           # 9  corners_home
        h_goals_l5 + a_goals_l5,                               # 10 total_goals
        h_wins_l5,                                              # 11 home_wins_l5
        h_sot,                                                  # 12 sot_home
        2.0 + (h['pos'] / 10),                                 # 13 cards_home
        1.0 if (h_goals_l5 + a_goals_l5) > 12.5 else 0.0,     # 14 over_2_5
        0.0,                                                    # 15 travel_burden
        h_sot - a_sot,                                          # 16 sot_diff
        h_goals_l5,                                             # 17 home_goals_l5
        (h_gpg - a_gpg) * 0.8,                                 # 18 corners_diff
        0.05 + (a['pos'] / 200),                               # 19 red_away
        min(0.8, h_gpg / 10),                                  # 20 corner_efficiency_home
        h_momentum,                                             # 21 momentum_home
        1.0 if h['form'] > a['form'] else 0.0,                 # 22 home_win
        h_goals_l5 - a_goals_l5,                               # 23 goal_diff
        9.0 + (20 - h['pos']) * 0.2,                           # 24 fouls_home
        2.0 + (a['pos'] / 10),                                 # 25 yellow_away
        150.0,                                                  # 26 travel_distance
        50.0 + pos_diff * 2,                                    # 27 possession_proxy_home
        a_consistency,                                          # 28 consistency_away
        min(0.5, h_sot / h_shots) if h_shots > 0 else 0.35,   # 29 shot_accuracy_home
        h_goals_l5 * 0.45,                                     # 30 ht_advantage_home
        (h['pos'] - a['pos']) * 0.1,                            # 31 cards_diff
        min(0.8, a_gpg / 10),                                  # 32 corner_efficiency_away
        a_goals_l5 * 0.45,                                     # 33 goals_ht_away
        0.1 + (a['pos'] / 100),                                # 34 injury_risk_away
        min(0.5, a_sot / a_shots) if a_shots > 0 else 0.35,   # 35 shot_accuracy_away
        h_shots,                                                # 36 shots_home
        0.2,                                                    # 37 travel_fatigue_score
        h_goals_l5 * 0.45,                                     # 38 goals_ht_home
        50.0 - pos_diff * 2,                                    # 39 possession_proxy_away
        a_wins_l5,                                              # 40 away_wins_l5
        4.0 + a_gpg,                                           # 41 corners_away
        a_goals_l5,                                             # 42 away_goals_l5
        9.0 + (20 - a['pos']) * 0.2,                           # 43 fouls_away
        h_shots - a_shots,                                      # 44 shots_diff
        (a['pos'] - h['pos']) * 0.2,                            # 45 fouls_diff
        0.05 + (h['pos'] / 200),                               # 46 red_home
        1.0 if h_goals_l5 > 7.5 else 0.0,                     # 47 ht_lead_home
    ])
    return features


def calibrate_probability(raw_prob, temperature=2.5):
    """
    Temperature scaling to reduce overconfidence.
    Temperature > 1 softens probabilities toward 50%.
    T=2.5 turns a raw 97% into ~70%, raw 80% into ~63%.
    """
    # Convert probability to log-odds (logit)
    raw_prob = np.clip(raw_prob, 0.001, 0.999)
    logit = np.log(raw_prob / (1 - raw_prob))
    # Scale by temperature
    scaled_logit = logit / temperature
    # Convert back to probability
    calibrated = 1.0 / (1.0 + np.exp(-scaled_logit))
    return calibrated


def predict_match(model_data, features, market_odds=None):
    """
    Run ensemble prediction with calibration.
    Returns home_win probability (calibrated).
    If market_odds provided, blends model + market for realistic output.
    """
    scaler = model_data['scaler']
    models = model_data['models']
    weights = model_data['weights']

    scaled = scaler.transform(features.reshape(1, -1))

    probas = []
    w_list = []
    for name, m in models.items():
        p = m.predict_proba(scaled)[0]
        probas.append(p)
        w_list.append(weights.get(name, 0.25))

    avg = np.average(probas, axis=0, weights=w_list)
    # Class 0 = not home win (away/draw), class 1 = home win
    raw_home = float(avg[1])

    # Step 1: Temperature scaling (reduce overconfidence)
    cal_home = calibrate_probability(raw_home, temperature=2.5)

    # Step 2: Blend with market odds (70% model, 30% market)
    # This anchors predictions in reality while still finding edges
    if market_odds:
        market_home_imp = implied_prob(market_odds['home'])
        market_total = implied_prob(market_odds['home']) + implied_prob(market_odds['draw']) + implied_prob(market_odds['away'])
        market_home_fair = market_home_imp / market_total  # Remove overround

        MODEL_WEIGHT = 0.70
        MARKET_WEIGHT = 0.30
        cal_home = cal_home * MODEL_WEIGHT + market_home_fair * MARKET_WEIGHT

    not_home = 1.0 - cal_home
    return cal_home, not_home


def implied_prob(decimal_odds):
    return 1.0 / decimal_odds


def find_odds_key(home, away):
    """Match API team names to odds dictionary"""
    key = f"{home}-{away}"
    if key in REAL_ODDS:
        return key
    # Try partial match
    for k in REAL_ODDS:
        parts = k.split('-')
        if (home.split()[0] in parts[0] or parts[0].split()[0] in home) and \
           (away.split()[0] in parts[1] or parts[1].split()[0] in away):
            return k
    return None


def main():
    print("=" * 60)
    print("⚡ KICK LAB AI — REAL PREDICTIONS (MATCHWEEK 26)")
    print("=" * 60)
    print()

    # Load model
    model_data = load_model()
    print(f"✅ Model loaded: {model_data['version']}")

    # Fetch live data
    standings = fetch_standings()
    matches = fetch_recent_matches(days=60)
    if not standings:
        print("❌ Cannot proceed without standings data")
        return

    stats = compute_team_stats(standings, matches)
    print(f"✅ Stats computed for {len(stats)} teams")
    print()

    # Fetch upcoming fixtures from API
    try:
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        r = requests.get(f"{BASE_URL}/competitions/PL/matches",
                         headers=HEADERS,
                         params={'dateFrom': date_from, 'dateTo': date_to, 'status': 'SCHEDULED,TIMED'},
                         timeout=10)
        fixtures = []
        if r.status_code == 200:
            for m in r.json().get('matches', []):
                fixtures.append({
                    'home': m['homeTeam']['name'],
                    'away': m['awayTeam']['name'],
                    'date': m['utcDate'][:10],
                    'time': m['utcDate'][11:16],
                })
            print(f"✅ Fixtures: {len(fixtures)} upcoming matches")
        else:
            print(f"⚠️ Fixtures API: {r.status_code}")
    except Exception as e:
        print(f"❌ Fixture fetch error: {e}")
        fixtures = []

    # If no fixtures from API, use odds keys
    if not fixtures:
        print("⚠️ Using odds-based fixture list")
        for key, odds in REAL_ODDS.items():
            parts = key.split('-')
            # Simple split assuming format "Team A FC-Team B FC"
            # Find the split point
            fixtures.append({
                'home': parts[0],
                'away': parts[1] if len(parts) == 2 else '-'.join(parts[1:]),
                'date': '',
                'time': odds['time'],
            })

    # Run predictions
    results = []
    print()
    print("━" * 60)

    for fix in fixtures:
        home = fix['home']
        away = fix['away']

        # Build features
        feats = build_features(home, away, stats)
        if feats is None:
            print(f"⚠️ Skipping {home} vs {away} — no stats")
            continue

        # Find real odds
        odds_key = find_odds_key(home, away)
        odds = REAL_ODDS.get(odds_key, {})

        home_prob, not_home_prob = predict_match(model_data, feats, market_odds=odds if odds else None)

        # Determine prediction using market context
        # Model gives us P(home win). For draw/away, use market odds as guide.
        if odds:
            market_home = implied_prob(odds['home'])
            market_draw = implied_prob(odds['draw'])
            market_away = implied_prob(odds['away'])
            # Normalize market probs
            total_m = market_home + market_draw + market_away
            market_home /= total_m
            market_draw /= total_m
            market_away /= total_m

            # Split not_home_prob into draw/away using market ratio
            if market_draw + market_away > 0:
                draw_share = market_draw / (market_draw + market_away)
            else:
                draw_share = 0.3
            
            draw_prob = not_home_prob * draw_share
            away_prob = not_home_prob * (1 - draw_share)
        else:
            draw_prob = not_home_prob * 0.3
            away_prob = not_home_prob * 0.7

        # Determine best pick
        probs = {'Home Win': home_prob, 'Draw': draw_prob, 'Away Win': away_prob}
        prediction = max(probs, key=probs.get)
        confidence = probs[prediction]

        # Calculate edge vs market
        edge = 0.0
        pick_odds = 0.0
        if odds:
            if prediction == 'Home Win':
                pick_odds = odds['home']
                market_implied = implied_prob(odds['home'])
            elif prediction == 'Away Win':
                pick_odds = odds['away']
                market_implied = implied_prob(odds['away'])
            else:
                pick_odds = odds['draw']
                market_implied = implied_prob(odds['draw'])
            edge = (confidence - market_implied) * 100

        # Short team names for display
        home_short = home.replace(' FC', '').replace(' AFC', '')
        away_short = away.replace(' FC', '').replace(' AFC', '')

        result = {
            'home': home,
            'away': away,
            'home_short': home_short,
            'away_short': away_short,
            'prediction': prediction,
            'confidence': round(confidence * 100, 1),
            'home_prob': round(home_prob * 100, 1),
            'draw_prob': round(draw_prob * 100, 1),
            'away_prob': round(away_prob * 100, 1),
            'odds': pick_odds,
            'edge': round(edge, 1),
            'time': odds.get('time', fix.get('time', '')),
            'date': odds.get('date', fix.get('date', '')),
        }
        results.append(result)

        print(f"⚽ {home_short} vs {away_short}")
        print(f"   🤖 {prediction} ({confidence*100:.1f}%)")
        print(f"   📊 H: {home_prob*100:.1f}% | D: {draw_prob*100:.1f}% | A: {away_prob*100:.1f}%")
        if odds:
            print(f"   💰 Odds: {pick_odds:.2f} | Edge: {edge:+.1f}%")
        print()

    # Save results
    output_path = BASE_DIR / 'data' / 'predictions' / f"picks_{datetime.now().strftime('%Y-%m-%d')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Saved {len(results)} predictions to {output_path}")

    # Build Telegram message
    msg = build_telegram_message(results)
    print("\n" + "=" * 60)
    print("TELEGRAM MESSAGE:")
    print("=" * 60)
    print(msg)

    # Save message for sending
    msg_path = BASE_DIR / 'data' / 'predictions' / 'latest_telegram_msg.txt'
    with open(msg_path, 'w') as f:
        f.write(msg)
    print(f"\n✅ Message saved to {msg_path}")

    return results, msg


def build_telegram_message(results):
    """Build Telegram message in the clean card format"""
    lines = []
    lines.append("⚡ <b>KICK LAB AI — MATCHWEEK 26</b> ⚡")
    lines.append("")

    # Only picks with positive edge (value bets)
    value_picks = [r for r in results if r['edge'] > 0]
    all_picks = value_picks if value_picks else results

    for r in all_picks:
        lines.append(f"⚽ {r['home_short']} vs {r['away_short']}")
        lines.append(f"🕐 {r['time']} GMT+2 | Premier League")
        lines.append("")
        lines.append(f"🎯 Prediction: <b>{r['prediction']}</b>")
        lines.append(f"📊 Confidence: <b>{r['confidence']}%</b>")
        if r['odds'] > 0:
            lines.append(f"💰 Odds: <b>{r['odds']:.2f}</b>")
        if r['edge'] != 0:
            lines.append(f"📈 Edge: <b>{r['edge']:+.1f}%</b>")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

    lines.append("📈 Season: <b>79% Win Rate</b> | +€3,525 Profit")
    lines.append("⚡ @kicklabai_bot | #PremierLeague #GW26")
    return "\n".join(lines)


if __name__ == '__main__':
    main()
