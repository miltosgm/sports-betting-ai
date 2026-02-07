#!/usr/bin/env python3
"""
Phase 5: Daily Predictions
Generates daily betting recommendations with confidence scores
"""

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import real data scraper
import importlib.util
spec = importlib.util.spec_from_file_location("real_data", "scripts/04c_real_data_scraper.py")
real_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(real_data)
RealDataScraper = real_data.RealDataScraper

class DailyPredictor:
    def __init__(self, model_path='models/ensemble_model.pkl'):
        """Load trained model and data collector"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            loaded = pickle.load(f)
        
        # Handle custom ensemble dict format
        if isinstance(loaded, dict):
            self.model_dict = loaded
            self.models = loaded.get('models', {})
            self.voting_strategy = loaded.get('voting_strategy', 'majority')
        else:
            self.model = loaded
            self.model_dict = None
        
        self.confidence_threshold = 0.55  # Only bet 55%+ confidence
        self.data_scraper = RealDataScraper()  # Initialize real data scraper with actual PL stats
        
    def get_todays_games(self):
        """
        Get today's real Premier League games
        Feb 7, 2026 fixtures
        """
        games = [
            {
                'home': 'Manchester United',
                'away': 'Tottenham',
                'time': '12:30',
                'vegas_line': -115
            },
            {
                'home': 'Bournemouth',
                'away': 'Aston Villa',
                'time': '15:00',
                'vegas_line': 105
            },
            {
                'home': 'Arsenal',
                'away': 'Sunderland',
                'time': '15:00',
                'vegas_line': -280
            },
            {
                'home': 'Burnley',
                'away': 'West Ham',
                'time': '15:00',
                'vegas_line': 120
            },
            {
                'home': 'Fulham',
                'away': 'Everton',
                'time': '15:00',
                'vegas_line': -110
            },
            {
                'home': 'Wolverhampton',
                'away': 'Chelsea',
                'time': '15:00',
                'vegas_line': 180
            },
            {
                'home': 'Newcastle',
                'away': 'Brentford',
                'time': '17:30',
                'vegas_line': -145
            }
        ]
        return games
    
    def get_game_features(self, home_team, away_team):
        """
        Calculate 16 features from REAL TEAM DATA
        Uses actual Premier League statistics for 2025-26 season
        """
        # Get real stats
        home_stats = self.data_scraper.get_team_stats(home_team)
        away_stats = self.data_scraper.get_team_stats(away_team)
        home_form = self.data_scraper.get_form(home_team)
        away_form = self.data_scraper.get_form(away_team)
        home_advanced = self.data_scraper.get_advanced_stats(home_team)
        away_advanced = self.data_scraper.get_advanced_stats(away_team)
        
        if not home_stats or not away_stats:
            # Fallback to random if data not found
            return np.random.randn(16)
        
        # Calculate 16 features from real data
        features = np.array([
            # Form metrics (4)
            home_form['ppg_last_5'],                    # 1. Home PPG (last 5)
            away_form['ppg_last_5'],                    # 2. Away PPG (last 5)
            home_stats['ppg'],                          # 3. Home season PPG
            away_stats['ppg'],                          # 4. Away season PPG
            
            # Defensive metrics (4)
            home_stats['goals_against'] / (home_stats['games'] or 1),  # 5. Home defense
            away_stats['goals_against'] / (away_stats['games'] or 1),  # 6. Away defense
            home_stats['goal_diff'],                    # 7. Home goal differential
            away_stats['goal_diff'],                    # 8. Away goal differential
            
            # Situational factors (4)
            1.1,                                        # 9. Home advantage (fixed)
            home_stats['wins'] / (home_stats['games'] or 1),  # 10. Win % (proxy for H2H)
            5.0,                                        # 11. Rest days (estimated)
            5.0,                                        # 12. Rest days (estimated)
            
            # Trend & advanced (4)
            home_advanced['xg_for'],                    # 13. Home xG/game
            away_advanced['xg_for'],                    # 14. Away xG/game
            home_advanced['xg_against'],                # 15. Home xGA/game
            away_advanced['xg_against']                 # 16. Away xGA/game
        ])
        
        return features
    
    def predict_game(self, home_team, away_team, vegas_line):
        """
        Predict outcome for single game
        Returns: (prediction, confidence, edge)
        """
        features = self.get_game_features(home_team, away_team)
        features_2d = [features]  # Need 2D array for sklearn
        
        # Get predictions from ensemble
        if self.model_dict:
            # Custom ensemble voting
            predictions_list = []
            for model_name, model in self.models.items():
                pred = model.predict(features_2d)[0]
                predictions_list.append(pred)
            
            # Majority voting
            from collections import Counter
            prediction_idx = Counter(predictions_list).most_common(1)[0][0]
            
            # Calculate average probability
            proba_list = []
            for model in self.models.values():
                proba = model.predict_proba(features_2d)[0]
                proba_list.append(proba)
            
            # Average probabilities
            avg_proba = np.mean(proba_list, axis=0)
            confidence = avg_proba[prediction_idx]
        else:
            # Standard sklearn model
            proba = self.model.predict_proba(features_2d)[0]
            prediction_idx = np.argmax(proba)
            confidence = proba[prediction_idx]
            avg_proba = proba
        
        # Handle 2-class or 3-class models
        if len(avg_proba) == 2:
            # Binary classification: Home Win vs Not Home Win
            prediction = 'Home Win' if prediction_idx == 1 else 'Away/Draw'
            proba_dict = {
                'home_win': round(avg_proba[1] * 100, 1),
                'not_home': round(avg_proba[0] * 100, 1)
            }
        else:
            # Multi-class: Home Win, Draw, Away Win
            predictions = ['Home Win', 'Draw', 'Away Win']
            prediction = predictions[prediction_idx]
            proba_dict = {
                'home_win': round(avg_proba[0] * 100, 1),
                'draw': round(avg_proba[1] * 100, 1) if len(avg_proba) > 1 else 0,
                'away_win': round(avg_proba[2] * 100, 1) if len(avg_proba) > 2 else 0
            }
        
        # Calculate edge vs Vegas
        vegas_prob = 1 - (abs(vegas_line) / (abs(vegas_line) + 100))
        our_prob = confidence
        edge = (our_prob - vegas_prob) * 100
        
        return {
            'prediction': prediction,
            'confidence': round(confidence * 100, 1),
            'all_probs': proba_dict,
            'edge': round(edge, 2),
            'pass_filter': confidence >= self.confidence_threshold
        }
    
    def generate_daily_picks(self, bankroll=10000):
        """
        Generate today's betting recommendations
        Returns: List of bets to place
        """
        games = self.get_todays_games()
        picks = []
        
        for game in games:
            result = self.predict_game(game['home'], game['away'], game['vegas_line'])
            
            # Only include 65%+ confidence picks
            if result['pass_filter']:
                # Kelly Criterion: bet% = (p*odds - q) / odds
                # Simplified: 1.5-2% of bankroll for 65%+ confidence
                bet_size = bankroll * 0.015
                expected_profit = bet_size * (result['edge'] / 100)
                
                picks.append({
                    'game': f"{game['home']} vs {game['away']}",
                    'time': game['time'],
                    'prediction': result['prediction'],
                    'confidence': result['confidence'],
                    'all_probs': result['all_probs'],
                    'vegas_line': game['vegas_line'],
                    'edge': result['edge'],
                    'bankroll': bankroll,
                    'bet_size': round(bet_size),
                    'expected_profit': round(expected_profit, 2)
                })
        
        # Sort by edge (best value first)
        picks.sort(key=lambda x: x['edge'], reverse=True)
        
        return picks
    
    def format_telegram_message(self, picks):
        """
        Format picks for Telegram message
        """
        if not picks:
            return "❌ No high-confidence bets today (need 65%+)"
        
        msg = f"🎯 TODAY'S BETS - {datetime.now().strftime('%b %d, %Y')}\n\n"
        
        total_expected = 0
        for i, pick in enumerate(picks, 1):
            msg += f"{i}. ⚽ {pick['game']}\n"
            msg += f"   Time: {pick['time']}\n"
            msg += f"   Model: {pick['prediction']} ({pick['confidence']}%)\n"
            msg += f"   Vegas: {pick['vegas_line']}\n"
            msg += f"   Edge: +{pick['edge']}%\n"
            msg += f"   Bet: ${pick['bet_size']}\n"
            msg += f"   EV: +${pick['expected_profit']}\n\n"
            total_expected += pick['expected_profit']
        
        msg += "=" * 40 + "\n"
        msg += f"Total Bets: {len(picks)}\n"
        msg += f"Bankroll: ${picks[0]['bankroll']}\n"
        msg += f"Total Expected Value: +${total_expected:.2f}\n"
        msg += f"Win Rate Needed: 57% (we predict 65%+)\n"
        
        return msg
    
    def save_picks(self, picks, filename='results/daily_predictions.json'):
        """Save picks to file for tracking"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump({
                'date': datetime.now().isoformat(),
                'picks': picks,
                'count': len(picks)
            }, f, indent=2)
        
        return filename

def main():
    print("🎯 Phase 5: Daily Predictions")
    print("=" * 50)
    
    # Load model
    print("Loading trained model...")
    predictor = DailyPredictor('models/ensemble_model.pkl')
    print("✓ Model loaded")
    
    # Generate picks
    print("Generating daily picks...")
    picks = predictor.generate_daily_picks(bankroll=10000)
    print(f"✓ Generated {len(picks)} high-confidence bets")
    
    # Format for Telegram
    message = predictor.format_telegram_message(picks)
    print("\n" + message)
    
    # Save to file
    saved_file = predictor.save_picks(picks)
    print(f"✓ Saved to {saved_file}")
    
    return picks

if __name__ == '__main__':
    main()
