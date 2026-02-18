#!/usr/bin/env python3
"""
Live Prediction Pipeline for Kick Lab AI
Fetches real fixtures, generates ML predictions, saves to JSON & database
"""

import sys
import os
import json
import pickle
import logging
from datetime import datetime, timedelta
from pathlib import Path
import requests
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / "models" / "ensemble_model_v5_proper.pkl"
PREDICTIONS_DIR = BASE_DIR / "data" / "predictions"
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)


class FixtureFetcher:
    """Fetches upcoming Premier League fixtures from free APIs"""
    
    def __init__(self):
        self.fixtures = []
    
    def fetch_from_football_data_org(self, days_ahead=7):
        """
        Fetch from football-data.org (free tier, no key needed for some endpoints)
        """
        try:
            # Premier League ID = 2021 (PL), 2014 (La Liga), etc.
            url = "https://api.football-data.org/v4/competitions/PL/matches"
            
            date_from = datetime.now().strftime('%Y-%m-%d')
            date_to = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            params = {
                'dateFrom': date_from,
                'dateTo': date_to,
                'status': 'SCHEDULED'
            }
            
            headers = {
                'X-Auth-Token': os.getenv('FOOTBALL_DATA_API_KEY', '')  # Optional key for higher limits
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                fixtures = []
                
                for match in data.get('matches', []):
                    fixture = {
                        'home_team': match['homeTeam']['name'],
                        'away_team': match['awayTeam']['name'],
                        'date': match['utcDate'][:10],  # YYYY-MM-DD
                        'time': match['utcDate'][11:16],  # HH:MM
                        'competition': 'Premier League',
                        'match_id': f"{match['homeTeam']['name']}-{match['awayTeam']['name']}-{match['utcDate'][:10]}".lower().replace(' ', '-')
                    }
                    fixtures.append(fixture)
                
                logger.info(f"✅ Fetched {len(fixtures)} fixtures from football-data.org")
                return fixtures
            else:
                logger.warning(f"football-data.org returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching from football-data.org: {e}")
            return []
    
    def fetch_from_api_football(self, days_ahead=7):
        """
        Fetch from API-Football (RapidAPI) - free tier: 100 calls/day
        """
        try:
            url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
            
            date_from = datetime.now().strftime('%Y-%m-%d')
            date_to = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            headers = {
                'X-RapidAPI-Key': os.getenv('RAPID_API_KEY', ''),
                'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
            }
            
            params = {
                'league': '39',  # Premier League
                'season': '2025',  # Adjust per year
                'from': date_from,
                'to': date_to,
                'status': 'NS'  # Not Started
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                fixtures = []
                
                for match in data.get('response', []):
                    fixture = {
                        'home_team': match['teams']['home']['name'],
                        'away_team': match['teams']['away']['name'],
                        'date': match['fixture']['date'][:10],
                        'time': match['fixture']['date'][11:16],
                        'competition': 'Premier League',
                        'match_id': f"{match['teams']['home']['name']}-{match['teams']['away']['name']}-{match['fixture']['date'][:10]}".lower().replace(' ', '-')
                    }
                    fixtures.append(fixture)
                
                logger.info(f"✅ Fetched {len(fixtures)} fixtures from API-Football")
                return fixtures
            else:
                logger.warning(f"API-Football returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching from API-Football: {e}")
            return []
    
    def get_fallback_fixtures(self):
        """
        Fallback: Return simulated upcoming fixtures for testing
        """
        logger.warning("⚠️ Using fallback fixtures (no live API available)")
        
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        fixtures = [
            {
                'home_team': 'Arsenal',
                'away_team': 'Manchester City',
                'date': tomorrow.strftime('%Y-%m-%d'),
                'time': '17:30',
                'competition': 'Premier League',
                'match_id': f"arsenal-manchester-city-{tomorrow.strftime('%Y-%m-%d')}"
            },
            {
                'home_team': 'Liverpool',
                'away_team': 'Chelsea',
                'date': tomorrow.strftime('%Y-%m-%d'),
                'time': '20:00',
                'competition': 'Premier League',
                'match_id': f"liverpool-chelsea-{tomorrow.strftime('%Y-%m-%d')}"
            },
            {
                'home_team': 'Manchester United',
                'away_team': 'Tottenham',
                'date': (tomorrow + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '15:00',
                'competition': 'Premier League',
                'match_id': f"manchester-united-tottenham-{(tomorrow + timedelta(days=1)).strftime('%Y-%m-%d')}"
            }
        ]
        
        return fixtures
    
    def fetch_fixtures(self, days_ahead=7):
        """
        Try multiple sources, return first successful one
        """
        logger.info(f"Fetching fixtures for next {days_ahead} days...")
        
        # Try football-data.org first (most reliable free API)
        fixtures = self.fetch_from_football_data_org(days_ahead)
        if fixtures:
            self.fixtures = fixtures
            return fixtures
        
        # Try API-Football as backup
        fixtures = self.fetch_from_api_football(days_ahead)
        if fixtures:
            self.fixtures = fixtures
            return fixtures
        
        # Fall back to simulated data
        fixtures = self.get_fallback_fixtures()
        self.fixtures = fixtures
        return fixtures


class LiveFeatureEngineer:
    """
    Lightweight feature engineering for upcoming matches
    Fetches REAL data from football-data.org API instead of using dummy defaults
    """
    
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_DATA_API_KEY', '')
        self.base_url = 'https://api.football-data.org/v4'
        self.headers = {'X-Auth-Token': self.api_key}
        
        # Cache to avoid hitting rate limits (10 req/min on free tier)
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # Fetch real data on init
        self.standings = self._fetch_standings()
        self.recent_matches = self._fetch_recent_matches()
        self.team_stats = self._compute_team_stats()
        
        logger.info(f"✅ LiveFeatureEngineer initialized with {len(self.team_stats)} teams")
    
    def _fetch_standings(self):
        """Fetch current Premier League standings"""
        cache_key = 'standings'
        if cache_key in self.cache:
            cached_time, data = self.cache[cache_key]
            if datetime.now().timestamp() - cached_time < self.cache_ttl:
                logger.info("📦 Using cached standings")
                return data
        
        try:
            url = f"{self.base_url}/competitions/PL/standings"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                standings = {}
                
                for table in data.get('standings', []):
                    if table['type'] == 'TOTAL':
                        for entry in table['table']:
                            team_name = entry['team']['name']
                            standings[team_name] = {
                                'position': entry['position'],
                                'played': entry['playedGames'],
                                'won': entry['won'],
                                'draw': entry['draw'],
                                'lost': entry['lost'],
                                'points': entry['points'],
                                'goals_for': entry['goalsFor'],
                                'goals_against': entry['goalsAgainst'],
                                'goal_difference': entry['goalDifference']
                            }
                
                logger.info(f"✅ Fetched standings for {len(standings)} teams")
                self.cache[cache_key] = (datetime.now().timestamp(), standings)
                return standings
            else:
                logger.warning(f"⚠️ API returned {response.status_code}, using fallback")
                return {}
        except Exception as e:
            logger.error(f"❌ Error fetching standings: {e}")
            return {}
    
    def _fetch_recent_matches(self, days_back=60):
        """Fetch recent Premier League matches for form calculation"""
        cache_key = 'recent_matches'
        if cache_key in self.cache:
            cached_time, data = self.cache[cache_key]
            if datetime.now().timestamp() - cached_time < self.cache_ttl:
                logger.info("📦 Using cached recent matches")
                return data
        
        try:
            date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            date_to = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/competitions/PL/matches"
            params = {
                'status': 'FINISHED',
                'dateFrom': date_from,
                'dateTo': date_to
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                matches = []
                
                for match in data.get('matches', []):
                    matches.append({
                        'date': match['utcDate'][:10],
                        'home_team': match['homeTeam']['name'],
                        'away_team': match['awayTeam']['name'],
                        'home_score': match['score']['fullTime']['home'],
                        'away_score': match['score']['fullTime']['away']
                    })
                
                # Sort by date (oldest first)
                matches = sorted(matches, key=lambda x: x['date'])
                
                logger.info(f"✅ Fetched {len(matches)} recent matches")
                self.cache[cache_key] = (datetime.now().timestamp(), matches)
                return matches
            else:
                logger.warning(f"⚠️ API returned {response.status_code}, using fallback")
                return []
        except Exception as e:
            logger.error(f"❌ Error fetching recent matches: {e}")
            return []
    
    def _compute_team_stats(self):
        """Compute per-team statistics from standings and recent matches"""
        if not self.standings:
            logger.warning("⚠️ No standings data, using fallback stats")
            return {}
        
        stats = {}
        
        for team, standing in self.standings.items():
            # Basic stats from standings
            played = standing['played']
            if played == 0:
                played = 1  # Avoid division by zero
            
            stats[team] = {
                'position': standing['position'],
                'points_per_game': standing['points'] / played,
                'goals_per_game': standing['goals_for'] / played,
                'goals_allowed_per_game': standing['goals_against'] / played,
                'win_rate': standing['won'] / played,
                'goal_difference': standing['goal_difference']
            }
            
            # Calculate home/away splits from recent matches
            home_games = [m for m in self.recent_matches if m['home_team'] == team]
            away_games = [m for m in self.recent_matches if m['away_team'] == team]
            
            # Home stats
            if home_games:
                home_wins = sum(1 for m in home_games if m['home_score'] > m['away_score'])
                home_goals = sum(m['home_score'] for m in home_games)
                home_conceded = sum(m['away_score'] for m in home_games)
                stats[team]['home_win_rate'] = home_wins / len(home_games)
                stats[team]['home_goals_per_game'] = home_goals / len(home_games)
                stats[team]['home_conceded_per_game'] = home_conceded / len(home_games)
            else:
                stats[team]['home_win_rate'] = stats[team]['win_rate']
                stats[team]['home_goals_per_game'] = stats[team]['goals_per_game']
                stats[team]['home_conceded_per_game'] = stats[team]['goals_allowed_per_game']
            
            # Away stats
            if away_games:
                away_wins = sum(1 for m in away_games if m['away_score'] > m['home_score'])
                away_goals = sum(m['away_score'] for m in away_games)
                away_conceded = sum(m['home_score'] for m in away_games)
                stats[team]['away_win_rate'] = away_wins / len(away_games)
                stats[team]['away_goals_per_game'] = away_goals / len(away_games)
                stats[team]['away_conceded_per_game'] = away_conceded / len(away_games)
            else:
                stats[team]['away_win_rate'] = stats[team]['win_rate']
                stats[team]['away_goals_per_game'] = stats[team]['goals_per_game']
                stats[team]['away_conceded_per_game'] = stats[team]['goals_allowed_per_game']
            
            # Recent form (last 5 games)
            team_games = [m for m in self.recent_matches if m['home_team'] == team or m['away_team'] == team]
            last_5 = team_games[-5:] if len(team_games) >= 5 else team_games
            
            if last_5:
                form_points = 0
                for m in last_5:
                    if m['home_team'] == team:
                        if m['home_score'] > m['away_score']:
                            form_points += 3
                        elif m['home_score'] == m['away_score']:
                            form_points += 1
                    else:
                        if m['away_score'] > m['home_score']:
                            form_points += 3
                        elif m['away_score'] == m['home_score']:
                            form_points += 1
                stats[team]['form_last_5_ppg'] = form_points / len(last_5)
            else:
                stats[team]['form_last_5_ppg'] = stats[team]['points_per_game']
        
        return stats
    
    def get_team_form(self, team, last_n=5):
        """Calculate team form from recent games"""
        if team in self.team_stats:
            return self.team_stats[team].get('form_last_5_ppg', 1.5)
        
        # Fallback if team not found
        logger.warning(f"⚠️ Team '{team}' not found in stats, using default")
        return 1.5
    
    def get_team_stats(self, team):
        """Get team statistics"""
        if team in self.team_stats:
            stats = self.team_stats[team]
            return {
                'goals_per_game': stats.get('goals_per_game', 1.5),
                'goals_allowed_per_game': stats.get('goals_allowed_per_game', 1.5),
                'possession': 50.0,  # Not available in free API, use neutral
                'shots_per_game': stats.get('goals_per_game', 1.5) * 8  # Estimate from goals
            }
        
        # Fallback
        logger.warning(f"⚠️ Team '{team}' not found in stats, using defaults")
        return {
            'goals_per_game': 1.5,
            'goals_allowed_per_game': 1.5,
            'possession': 50.0,
            'shots_per_game': 12.0
        }
    
    def engineer_features(self, home_team, away_team):
        """
        Generate feature vector for upcoming match using REAL team data
        Returns 48 features matching the v5_proper model
        """
        # Get REAL team stats from API
        home_data = self.team_stats.get(home_team, {})
        away_data = self.team_stats.get(away_team, {})
        
        # Use defaults only if team not found
        if not home_data:
            logger.warning(f"⚠️ No data for {home_team}, using defaults")
            home_data = {
                'position': 10, 'points_per_game': 1.5, 'goals_per_game': 1.5,
                'goals_allowed_per_game': 1.5, 'win_rate': 0.4, 'goal_difference': 0,
                'home_win_rate': 0.5, 'home_goals_per_game': 1.7, 'home_conceded_per_game': 1.3,
                'away_win_rate': 0.3, 'away_goals_per_game': 1.3, 'away_conceded_per_game': 1.7,
                'form_last_5_ppg': 1.5
            }
        
        if not away_data:
            logger.warning(f"⚠️ No data for {away_team}, using defaults")
            away_data = {
                'position': 10, 'points_per_game': 1.5, 'goals_per_game': 1.5,
                'goals_allowed_per_game': 1.5, 'win_rate': 0.4, 'goal_difference': 0,
                'home_win_rate': 0.5, 'home_goals_per_game': 1.7, 'home_conceded_per_game': 1.3,
                'away_win_rate': 0.3, 'away_goals_per_game': 1.3, 'away_conceded_per_game': 1.7,
                'form_last_5_ppg': 1.5
            }
        
        # Extract home team metrics
        home_form_ppg = home_data['form_last_5_ppg']
        home_goals_pg = home_data['home_goals_per_game']  # Use HOME-specific
        home_conceded_pg = home_data['home_conceded_per_game']
        home_win_rate = home_data['home_win_rate']
        home_position = home_data['position']
        
        # Extract away team metrics
        away_form_ppg = away_data['form_last_5_ppg']
        away_goals_pg = away_data['away_goals_per_game']  # Use AWAY-specific
        away_conceded_pg = away_data['away_conceded_per_game']
        away_win_rate = away_data['away_win_rate']
        away_position = away_data['position']
        
        # Calculate derived metrics (5 games projection)
        home_goals_l5 = home_goals_pg * 5
        away_goals_l5 = away_goals_pg * 5
        home_conceded_l5 = home_conceded_pg * 5
        away_conceded_l5 = away_conceded_pg * 5
        home_wins_l5 = home_win_rate * 5
        away_wins_l5 = away_win_rate * 5
        
        # Estimate shots from goals (typical conversion ~15%)
        home_shots_pg = home_goals_pg / 0.15
        away_shots_pg = away_goals_pg / 0.15
        home_sot_pg = home_shots_pg * 0.4  # ~40% shots on target
        away_sot_pg = away_shots_pg * 0.4
        
        # Consistency (based on goal difference stability)
        home_consistency = min(0.9, 0.5 + abs(home_data['goal_difference']) * 0.02)
        away_consistency = min(0.9, 0.5 + abs(away_data['goal_difference']) * 0.02)
        
        # Momentum (form relative to season average)
        home_momentum = home_form_ppg / max(0.1, home_data['points_per_game'])
        away_momentum = away_form_ppg / max(0.1, away_data['points_per_game'])
        
        # Position differential (quality gap)
        position_diff = away_position - home_position  # Positive = home team better
        
        # Build 48-feature vector with REAL differentiated data per team
        features = np.array([
            home_consistency,                           # 0. consistency_home
            away_sot_pg,                                # 1. sot_away
            2.0 + (away_position / 10),                 # 2. cards_away (worse teams = more cards)
            away_shots_pg,                              # 3. shots_away
            2.0 + (home_position / 10),                 # 4. yellow_home
            home_goals_l5 * 0.55,                       # 5. goals_2h_home (slightly more 2nd half)
            0.1 + (home_position / 100),                # 6. injury_risk_home
            away_momentum,                              # 7. momentum_away
            away_goals_l5 * 0.55,                       # 8. goals_2h_away
            4.0 + home_goals_pg,                        # 9. corners_home (correlates with attack)
            home_goals_l5 + away_goals_l5,              # 10. total_goals
            home_wins_l5,                               # 11. home_wins_l5
            home_sot_pg,                                # 12. sot_home
            2.0 + (home_position / 10),                 # 13. cards_home
            1.0 if (home_goals_l5 + away_goals_l5) > 12.5 else 0.0,  # 14. over_2_5
            0.0,                                        # 15. travel_burden
            home_sot_pg - away_sot_pg,                  # 16. sot_diff
            home_goals_l5,                              # 17. home_goals_l5
            (home_goals_pg - away_goals_pg) * 0.8,      # 18. corners_diff (proxy)
            0.05 + (away_position / 200),               # 19. red_away
            min(0.8, home_goals_pg / 10),               # 20. corner_efficiency_home
            home_momentum,                              # 21. momentum_home
            1.0 if home_form_ppg > away_form_ppg else 0.0,  # 22. home_win
            home_goals_l5 - away_goals_l5,              # 23. goal_diff
            9.0 + (20 - home_position) * 0.2,           # 24. fouls_home (better teams foul less)
            2.0 + (away_position / 10),                 # 25. yellow_away
            150.0,                                      # 26. travel_distance (average)
            50.0 + position_diff * 2,                   # 27. possession_proxy_home (better = more)
            away_consistency,                           # 28. consistency_away
            min(0.5, home_sot_pg / home_shots_pg) if home_shots_pg > 0 else 0.35,  # 29. shot_accuracy_home
            home_goals_l5 * 0.45,                       # 30. ht_advantage_home (first half)
            (home_position - away_position) * 0.1,      # 31. cards_diff
            min(0.8, away_goals_pg / 10),               # 32. corner_efficiency_away
            away_goals_l5 * 0.45,                       # 33. goals_ht_away
            0.1 + (away_position / 100),                # 34. injury_risk_away
            min(0.5, away_sot_pg / away_shots_pg) if away_shots_pg > 0 else 0.35,  # 35. shot_accuracy_away
            home_shots_pg,                              # 36. shots_home
            0.2,                                        # 37. travel_fatigue_score
            home_goals_l5 * 0.45,                       # 38. goals_ht_home
            50.0 - position_diff * 2,                   # 39. possession_proxy_away
            away_wins_l5,                               # 40. away_wins_l5
            4.0 + away_goals_pg,                        # 41. corners_away
            away_goals_l5,                              # 42. away_goals_l5
            9.0 + (20 - away_position) * 0.2,           # 43. fouls_away
            home_shots_pg - away_shots_pg,              # 44. shots_diff
            (away_position - home_position) * 0.2,      # 45. fouls_diff
            0.05 + (home_position / 200),               # 46. red_home
            1.0 if home_goals_l5 > 7.5 else 0.0         # 47. ht_lead_home (strong attack)
        ])
        
        logger.info(f"🎯 Features for {home_team} (pos {home_position}, {home_goals_pg:.1f}gpg) vs {away_team} (pos {away_position}, {away_goals_pg:.1f}gpg)")
        
        return features


class PredictionGenerator:
    """Generates predictions using the trained ML model"""
    
    def __init__(self, model_path=MODEL_PATH):
        self.model = self._load_model(model_path)
        self.feature_engineer = LiveFeatureEngineer()
    
    def _load_model(self, model_path):
        """Load the trained ensemble model"""
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"✅ Loaded model from {model_path}")
        return model
    
    def predict_match(self, home_team, away_team):
        """
        Generate prediction for a single match
        Returns: dict with prediction details
        """
        # Engineer features
        features = self.feature_engineer.engineer_features(home_team, away_team)
        features_2d = features.reshape(1, -1)
        
        # Handle ensemble model structure
        if isinstance(self.model, dict):
            # Custom ensemble with multiple models
            models = self.model.get('models', {})
            weights = self.model.get('weights', {})
            
            proba_list = []
            weight_list = []
            
            for model_name, model in models.items():
                proba = model.predict_proba(features_2d)[0]
                proba_list.append(proba)
                weight = weights.get(model_name, 1.0 / len(models))
                weight_list.append(weight)
            
            # Weighted average
            avg_proba = np.average(proba_list, axis=0, weights=weight_list)
        else:
            # Standard sklearn model
            avg_proba = self.model.predict_proba(features_2d)[0]
        
        # Interpret probabilities
        if len(avg_proba) == 3:
            # 3-class: Home, Draw, Away
            home_prob = avg_proba[0]
            draw_prob = avg_proba[1]
            away_prob = avg_proba[2]
        else:
            # Binary classification fallback
            home_prob = avg_proba[1] if len(avg_proba) > 1 else 0.5
            draw_prob = 0.0
            away_prob = avg_proba[0] if len(avg_proba) > 1 else 0.5
        
        # Determine prediction
        max_prob = max(home_prob, draw_prob, away_prob)
        if max_prob == home_prob:
            prediction = "Home Win"
        elif max_prob == away_prob:
            prediction = "Away Win"
        else:
            prediction = "Draw"
        
        confidence = max_prob
        
        # Estimate odds from probabilities (simplified)
        home_odds = 1 / home_prob if home_prob > 0.01 else 100
        draw_odds = 1 / draw_prob if draw_prob > 0.01 else 100
        away_odds = 1 / away_prob if away_prob > 0.01 else 100
        
        # Calculate expected value (simplified)
        # Assume bookmaker odds are 5% worse than fair odds
        fair_odds = 1 / max_prob
        bookmaker_odds = fair_odds * 0.95
        ev = (max_prob * bookmaker_odds) - 1
        edge_pct = ev * 100
        
        # Value bet if edge > 5%
        value_bet = bool(edge_pct > 5)
        
        # Generate AI reasoning
        reasoning = self._generate_reasoning(home_team, away_team, features, home_prob, away_prob)
        
        return {
            'prediction': str(prediction),
            'confidence': float(round(confidence, 4)),
            'probabilities': {
                'home': float(round(home_prob, 4)),
                'draw': float(round(draw_prob, 4)),
                'away': float(round(away_prob, 4))
            },
            'suggested_odds': {
                'home': float(round(home_odds, 2)),
                'draw': float(round(draw_odds, 2)),
                'away': float(round(away_odds, 2))
            },
            'value_bet': bool(value_bet),
            'edge_pct': float(round(edge_pct, 2)),
            'ai_reasoning': [str(r) for r in reasoning],
            # Additional predictions (simplified)
            'over_25': {
                'prediction': bool(home_prob + away_prob > 0.6),
                'confidence': float(round((home_prob + away_prob) * 0.8, 4))
            },
            'btts': {
                'prediction': bool(home_prob * away_prob > 0.15),
                'confidence': float(round(min(home_prob, away_prob) * 2, 4))
            }
        }
    
    def _generate_reasoning(self, home_team, away_team, features, home_prob, away_prob):
        """Generate human-readable reasoning"""
        reasoning = []
        
        # Form analysis
        home_form = features[0]  # Last 5 PPG
        away_form = features[2]
        
        if home_form > 2.0:
            reasoning.append(f"{home_team} excellent home form: {home_form:.1f} PPG")
        elif home_form < 1.0:
            reasoning.append(f"{home_team} struggling at home: {home_form:.1f} PPG")
        
        if away_form > 2.0:
            reasoning.append(f"{away_team} strong away form: {away_form:.1f} PPG")
        elif away_form < 1.0:
            reasoning.append(f"{away_team} poor away record: {away_form:.1f} PPG")
        
        # Head-to-head context
        if home_prob > 0.6:
            reasoning.append(f"Strong home advantage: {home_prob*100:.0f}% win probability")
        elif away_prob > 0.6:
            reasoning.append(f"Away team favored: {away_prob*100:.0f}% win probability")
        
        # Defensive analysis
        home_def = features[4]
        away_def = features[5]
        
        if home_def < 1.0:
            reasoning.append(f"{home_team} solid defense: {home_def:.2f} GA/game")
        if away_def > 1.5:
            reasoning.append(f"{away_team} leaky defense: {away_def:.2f} GA/game")
        
        return reasoning[:4]  # Limit to top 4 insights


class PredictionPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self):
        self.fixture_fetcher = FixtureFetcher()
        self.predictor = PredictionGenerator()
    
    def run(self, days_ahead=7):
        """
        Run complete prediction pipeline
        1. Fetch fixtures
        2. Generate predictions
        3. Save to JSON
        4. Save to database (optional)
        """
        logger.info("=" * 60)
        logger.info("🚀 LIVE PREDICTION PIPELINE")
        logger.info("=" * 60)
        
        # Step 1: Fetch fixtures
        fixtures = self.fixture_fetcher.fetch_fixtures(days_ahead)
        logger.info(f"📅 Found {len(fixtures)} upcoming fixtures")
        
        # Step 2: Generate predictions
        predictions = []
        for fixture in fixtures:
            logger.info(f"🔮 Predicting: {fixture['home_team']} vs {fixture['away_team']}")
            
            prediction = self.predictor.predict_match(
                fixture['home_team'],
                fixture['away_team']
            )
            
            # Combine fixture + prediction
            full_prediction = {
                'match_id': fixture['match_id'],
                'home_team': fixture['home_team'],
                'away_team': fixture['away_team'],
                'date': fixture['date'],
                'kickoff': fixture['time'],
                'competition': fixture['competition'],
                **prediction
            }
            
            predictions.append(full_prediction)
            
            logger.info(f"  ✅ {prediction['prediction']} ({prediction['confidence']*100:.1f}% confidence)")
        
        # Step 3: Save to JSON
        output = {
            'generated_at': datetime.now().isoformat(),
            'model_version': 'v5_proper',
            'predictions': predictions
        }
        
        output_file = PREDICTIONS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_predictions.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"💾 Saved predictions to {output_file}")
        
        # Step 4: Save to database (if available)
        try:
            self._save_to_database(predictions)
        except Exception as e:
            logger.warning(f"⚠️ Could not save to database: {e}")
        
        logger.info("=" * 60)
        logger.info(f"✅ PIPELINE COMPLETE: {len(predictions)} predictions generated")
        logger.info("=" * 60)
        
        return predictions
    
    def _save_to_database(self, predictions):
        """Save predictions to SQLite database"""
        try:
            from backend.app import db, Prediction
            
            for pred in predictions:
                # Check if prediction already exists
                existing = Prediction.query.filter_by(match_id=pred['match_id']).first()
                
                if existing:
                    logger.info(f"  ⚠️ Prediction already exists for {pred['match_id']}, skipping")
                    continue
                
                # Create new prediction record
                db_pred = Prediction(
                    match_id=pred['match_id'],
                    date=datetime.fromisoformat(pred['date']),
                    home_team=pred['home_team'],
                    away_team=pred['away_team'],
                    league='Premier League',
                    predicted_winner=pred['prediction'],
                    confidence=pred['confidence'] * 100,  # Convert to 0-100 scale
                    expected_value=pred['edge_pct'],
                    home_win_prob=pred['probabilities']['home'],
                    draw_prob=pred['probabilities']['draw'],
                    away_win_prob=pred['probabilities']['away'],
                    home_odds=pred['suggested_odds']['home'],
                    draw_odds=pred['suggested_odds']['draw'],
                    away_odds=pred['suggested_odds']['away'],
                    actual_result='Pending'
                )
                
                db.session.add(db_pred)
            
            db.session.commit()
            logger.info("✅ Saved predictions to database")
            
        except ImportError:
            logger.warning("⚠️ Database module not available, skipping DB save")
        except Exception as e:
            logger.error(f"❌ Database error: {e}")


def main():
    pipeline = PredictionPipeline()
    predictions = pipeline.run(days_ahead=7)
    
    # Print summary
    print("\n📊 PREDICTION SUMMARY:")
    print(f"Total predictions: {len(predictions)}")
    
    value_bets = [p for p in predictions if p['value_bet']]
    print(f"Value bets (5%+ edge): {len(value_bets)}")
    
    high_conf = [p for p in predictions if p['confidence'] > 0.7]
    print(f"High confidence (>70%): {len(high_conf)}")
    
    return predictions


if __name__ == '__main__':
    main()
