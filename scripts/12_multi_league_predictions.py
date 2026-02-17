"""
Multi-league predictions - expand beyond EPL to LaLiga, Serie A, Bundesliga, Ligue 1
Using the same V5 Proper ensemble model architecture
"""

import pandas as pd
import numpy as np
import pickle
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# League configurations
LEAGUES = {
    'EPL': {
        'name': 'English Premier League',
        'api': 'https://api.football-data.org/v4/competitions/PL',
        'matches_endpoint': '/matches?status=SCHEDULED',
        'injury_source': 'ESPN',
        'timezone': 'UTC',
        'teams': 20,
        'matches_per_season': 380
    },
    'LaLiga': {
        'name': 'Spanish La Liga',
        'api': 'https://api.football-data.org/v4/competitions/PD',
        'matches_endpoint': '/matches?status=SCHEDULED',
        'injury_source': 'Transfermarkt',
        'timezone': 'UTC+1',
        'teams': 20,
        'matches_per_season': 380
    },
    'Serie A': {
        'name': 'Italian Serie A',
        'api': 'https://api.football-data.org/v4/competitions/SA',
        'matches_endpoint': '/matches?status=SCHEDULED',
        'injury_source': 'Transfermarkt',
        'timezone': 'UTC+1',
        'teams': 20,
        'matches_per_season': 380
    },
    'Bundesliga': {
        'name': 'German Bundesliga',
        'api': 'https://api.football-data.org/v4/competitions/BL1',
        'matches_endpoint': '/matches?status=SCHEDULED',
        'injury_source': 'Transfermarkt',
        'timezone': 'UTC+1',
        'teams': 18,
        'matches_per_season': 306
    },
    'Ligue 1': {
        'name': 'French Ligue 1',
        'api': 'https://api.football-data.org/v4/competitions/FL1',
        'matches_endpoint': '/matches?status=SCHEDULED',
        'injury_source': 'ESPN',
        'timezone': 'UTC+1',
        'teams': 20,
        'matches_per_season': 380
    }
}

# Model paths
MODEL_DIR = Path(__file__).parent.parent / 'models'
V5_MODEL = MODEL_DIR / 'ensemble_model_v5_proper.pkl'
FEATURE_SCALER = MODEL_DIR / 'feature_scaler_v5.pkl'


class MultiLeaguePredictor:
    def __init__(self):
        self.model = self._load_model()
        self.scaler = self._load_scaler()
        self.api_key = os.getenv('FOOTBALL_DATA_API_KEY', '')
    
    def _load_model(self):
        """Load ensemble model"""
        try:
            with open(V5_MODEL, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f'Error loading model: {e}')
            return None
    
    def _load_scaler(self):
        """Load feature scaler"""
        try:
            with open(FEATURE_SCALER, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f'Error loading scaler: {e}')
            return None
    
    def fetch_matches(self, league_code):
        """Fetch upcoming matches for league"""
        league = LEAGUES[league_code]
        url = league['api'] + league['matches_endpoint']
        
        headers = {'X-Auth-Token': self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            return data.get('matches', [])
        except Exception as e:
            print(f'Error fetching {league_code} matches: {e}')
            return []
    
    def fetch_injuries(self, league_code, team):
        """Fetch injury data from multiple sources"""
        # Placeholder - integrate with Transfermarkt/ESPN APIs
        injuries = {
            team: []
        }
        return injuries
    
    def extract_features(self, match, league_code, historical_data):
        """Extract features for prediction"""
        
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        
        features = []
        
        # 1. Travel distance (calculate based on stadium locations)
        travel_distance = self._calculate_travel_distance(home_team, away_team, league_code)
        features.append(travel_distance)
        
        # 2. Recent form (L5 games)
        home_form = self._get_recent_form(home_team, league_code, historical_data)
        away_form = self._get_recent_form(away_team, league_code, historical_data)
        features.extend([home_form, away_form])
        
        # 3. Injuries
        home_key_injuries = self._count_key_injuries(home_team, league_code)
        away_key_injuries = self._count_key_injuries(away_team, league_code)
        features.extend([home_key_injuries, away_key_injuries])
        
        # 4. Home advantage (constant across leagues)
        features.append(1.0)
        
        # 5. Squad depth
        home_depth = self._get_squad_depth(home_team, league_code)
        away_depth = self._get_squad_depth(away_team, league_code)
        features.extend([home_depth, away_depth])
        
        # 6. Rest days (days since last match)
        home_rest = self._get_rest_days(home_team, league_code)
        away_rest = self._get_rest_days(away_team, league_code)
        features.extend([home_rest, away_rest])
        
        # 7. Head-to-head
        h2h_home_wins = self._get_h2h_record(home_team, away_team, league_code)
        features.append(h2h_home_wins)
        
        # 8. League difficulty (strength of schedule)
        features.append(self._get_league_difficulty(league_code))
        
        return np.array(features).reshape(1, -1)
    
    def _calculate_travel_distance(self, home_team, away_team, league_code):
        """Calculate travel distance"""
        # Placeholder - would integrate with stadium coordinates database
        return np.random.uniform(0, 500)  # For demo
    
    def _get_recent_form(self, team, league_code, historical_data):
        """Get recent form (points from last 5 matches)"""
        # Query historical data
        return np.random.uniform(0, 5)  # For demo
    
    def _count_key_injuries(self, team, league_code):
        """Count key player injuries"""
        # Query injury database
        return np.random.randint(0, 3)  # For demo
    
    def _get_squad_depth(self, team, league_code):
        """Get squad depth score"""
        return np.random.uniform(0, 10)  # For demo
    
    def _get_rest_days(self, team, league_code):
        """Get rest days since last match"""
        return np.random.uniform(3, 7)  # For demo
    
    def _get_h2h_record(self, home_team, away_team, league_code):
        """Get head-to-head record"""
        return np.random.uniform(0, 1)  # For demo
    
    def _get_league_difficulty(self, league_code):
        """Get league strength difficulty"""
        difficulty = {
            'EPL': 0.95,
            'LaLiga': 0.90,
            'Serie A': 0.88,
            'Bundesliga': 0.87,
            'Ligue 1': 0.85
        }
        return difficulty.get(league_code, 0.88)
    
    def predict_match(self, match, league_code, historical_data):
        """Predict match outcome"""
        
        if not self.model or not self.scaler:
            return None
        
        try:
            features = self.extract_features(match, league_code, historical_data)
            features_scaled = self.scaler.transform(features)
            
            # Get probability predictions
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Assuming [Home, Draw, Away]
            home_prob = probabilities[0]
            draw_prob = probabilities[1]
            away_prob = probabilities[2]
            
            # Determine winner
            max_prob_idx = np.argmax(probabilities)
            prediction_map = {0: 'Home', 1: 'Draw', 2: 'Away'}
            predicted_winner = prediction_map[max_prob_idx]
            confidence = max(probabilities) * 100
            
            return {
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'predicted_winner': predicted_winner,
                'confidence': confidence,
                'home_prob': home_prob,
                'draw_prob': draw_prob,
                'away_prob': away_prob,
                'match_date': match['utcDate'],
                'league': league_code
            }
        except Exception as e:
            print(f'Error predicting match: {e}')
            return None
    
    def predict_all_leagues(self):
        """Generate predictions for all leagues"""
        
        all_predictions = []
        
        for league_code in LEAGUES.keys():
            print(f'Generating predictions for {league_code}...')
            
            matches = self.fetch_matches(league_code)
            
            # Filter to next 7 days
            today = datetime.utcnow()
            week_future = today + timedelta(days=7)
            
            for match in matches:
                match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
                
                if match_date > today and match_date < week_future:
                    prediction = self.predict_match(match, league_code, {})
                    
                    if prediction:
                        all_predictions.append(prediction)
        
        return all_predictions
    
    def save_predictions(self, predictions):
        """Save predictions to file and database"""
        
        # Save to JSON
        output_file = Path(__file__).parent.parent / 'data' / f'multi_league_predictions_{datetime.now().strftime("%Y%m%d")}.json'
        
        with open(output_file, 'w') as f:
            json.dump(predictions, f, indent=2, default=str)
        
        print(f'Saved {len(predictions)} predictions to {output_file}')
        
        # Save to database (if Flask app context available)
        try:
            from backend.app import db, Prediction
            
            for pred in predictions:
                prediction = Prediction(
                    match_id=f"{pred['home_team']}_{pred['away_team']}_{pred['match_date']}",
                    date=datetime.fromisoformat(pred['match_date'].replace('Z', '+00:00')),
                    home_team=pred['home_team'],
                    away_team=pred['away_team'],
                    league=pred['league'],
                    predicted_winner=pred['predicted_winner'],
                    confidence=pred['confidence'],
                    home_win_prob=pred['home_prob'],
                    draw_prob=pred['draw_prob'],
                    away_win_prob=pred['away_prob'],
                    actual_result='Pending'
                )
                db.session.add(prediction)
            
            db.session.commit()
            print(f'Saved predictions to database')
        except Exception as e:
            print(f'Error saving to database: {e}')


def main():
    """Generate multi-league predictions"""
    predictor = MultiLeaguePredictor()
    predictions = predictor.predict_all_leagues()
    
    print(f'\n Generated {len(predictions)} predictions across all leagues:')
    print(f'  • EPL: {len([p for p in predictions if p["league"] == "EPL"])} matches')
    print(f'  • LaLiga: {len([p for p in predictions if p["league"] == "LaLiga"])} matches')
    print(f'  • Serie A: {len([p for p in predictions if p["league"] == "Serie A"])} matches')
    print(f'  • Bundesliga: {len([p for p in predictions if p["league"] == "Bundesliga"])} matches')
    print(f'  • Ligue 1: {len([p for p in predictions if p["league"] == "Ligue 1"])} matches')
    
    predictor.save_predictions(predictions)
    
    # Send notifications
    print('\nSending notifications...')
    # Email, Telegram, SMS would be called here


if __name__ == '__main__':
    import os
    main()
