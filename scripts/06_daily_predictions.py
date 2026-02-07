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

class DailyPredictor:
    def __init__(self, model_path='models/ensemble_model.pkl'):
        """Load trained model"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        self.confidence_threshold = 0.65  # Only bet 65%+ confidence
        
    def get_todays_games(self):
        """
        Get today's Premier League games
        TODO: Implement actual API call to get live games
        """
        # For now, return mock data for testing
        games = [
            {
                'home': 'Arsenal',
                'away': 'Liverpool',
                'time': '15:00',
                'vegas_line': -130
            },
            {
                'home': 'Man City',
                'away': 'Chelsea',
                'time': '17:30',
                'vegas_line': -180
            },
            {
                'home': 'Man United',
                'away': 'Brighton',
                'time': '20:00',
                'vegas_line': -120
            }
        ]
        return games
    
    def get_game_features(self, home_team, away_team):
        """
        Calculate 16 features for a game
        TODO: Implement actual feature engineering from live data
        """
        # Mock features for testing
        features = np.array([
            np.random.uniform(0.4, 0.8),  # Home form
            np.random.uniform(0.3, 0.7),  # Away form
            np.random.uniform(1.0, 2.0),  # Home defense
            np.random.uniform(0.8, 1.8),  # Away defense
            np.random.uniform(0.5, 1.0),  # H2H advantage
            np.random.uniform(0.0, 5.0),  # Winning streak
            np.random.uniform(1.0, 1.3),  # Home advantage
            np.random.uniform(2, 8),      # Rest days home
            np.random.uniform(2, 8),      # Rest days away
            np.random.uniform(0.3, 0.8),  # Recent wins
            np.random.uniform(0.2, 0.6),  # Clean sheets
            np.random.uniform(0.0, 4.0),  # Losing streak
            np.random.uniform(0.0, 1.0),  # O/U trend
            np.random.uniform(-2, 2),     # Line movement
            np.random.uniform(0.5, 2.5),  # Goals scored avg
            np.random.uniform(0.3, 1.5)   # Goals conceded avg
        ])
        return features
    
    def predict_game(self, home_team, away_team, vegas_line):
        """
        Predict outcome for single game
        Returns: (prediction, confidence, edge)
        """
        features = self.get_game_features(home_team, away_team)
        
        # Get prediction probabilities
        proba = self.model.predict_proba([features])[0]
        
        # Classes: 0=Home Win, 1=Draw, 2=Away Win
        prediction_idx = np.argmax(proba)
        confidence = proba[prediction_idx]
        
        predictions = ['Home Win', 'Draw', 'Away Win']
        prediction = predictions[prediction_idx]
        
        # Calculate edge vs Vegas
        # Vegas implied probability (simplified)
        vegas_prob = 1 - (abs(vegas_line) / (abs(vegas_line) + 100))
        our_prob = confidence
        edge = (our_prob - vegas_prob) * 100
        
        return {
            'prediction': prediction,
            'confidence': round(confidence * 100, 1),
            'all_probs': {
                'home_win': round(proba[0] * 100, 1),
                'draw': round(proba[1] * 100, 1),
                'away_win': round(proba[2] * 100, 1)
            },
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
