
import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

class LineMovementTracker:
    """Track betting line movement across sportsbooks"""
    
    def __init__(self):
        self.data_dir = Path("line_movement")
        self.data_dir.mkdir(exist_ok=True)
        
        # Sample sportsbooks (real API would track all)
        self.sportsbooks = {
            'bet365': 'https://api.bet365.com',
            'draftkings': 'https://api.draftkings.com',
            'fanduel': 'https://api.fanduel.com',
            'betmgm': 'https://api.betmgm.com',
        }
    
    def fetch_current_odds(self, match_id, home, away):
        """Fetch current odds from multiple books"""
        try:
            odds_data = {
                'match_id': match_id,
                'home': home,
                'away': away,
                'timestamp': datetime.now().isoformat(),
                'books': {}
            }
            
            # In production: call real APIs
            # For now: use cached/mock data
            odds_data['books'] = {
                'bet365': {'home': 1.95, 'away': 1.95},
                'draftkings': {'home': 1.94, 'away': 1.96},
                'fanduel': {'home': 1.96, 'away': 1.94},
            }
            
            return odds_data
        except Exception as e:
            print(f"Error fetching odds: {e}")
            return None
    
    def calculate_line_movement(self, opening_odds, current_odds):
        """Calculate line movement from opening to current"""
        movement = {
            'opening': opening_odds,
            'current': current_odds,
            'change': current_odds - opening_odds,
            'direction': 'up' if current_odds > opening_odds else 'down',
            'percent_change': ((current_odds - opening_odds) / opening_odds) * 100
        }
        return movement
    
    def detect_sharp_money(self, odds_data, threshold=0.05):
        """Detect sharp money (>5% line movement)"""
        books = odds_data['books']
        movements = {}
        
        for book, odds in books.items():
            # Track vs average
            avg = sum(o['home'] for o in books.values()) / len(books)
            movement = abs(odds['home'] - avg) / avg
            
            if movement > threshold:
                movements[book] = {
                    'movement': movement,
                    'odds': odds['home'],
                    'vs_avg': odds['home'] - avg,
                    'sharp_signal': 'yes' if movement > threshold else 'no'
                }
        
        return movements
    
    def log_match_odds(self, match_id, odds_data):
        """Log odds to file for tracking"""
        match_file = self.data_dir / f"{match_id}_odds.json"
        
        if match_file.exists():
            with open(match_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(odds_data)
        
        with open(match_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_line_movement_report(self, match_id):
        """Generate line movement report for a match"""
        match_file = self.data_dir / f"{match_id}_odds.json"
        
        if not match_file.exists():
            return None
        
        with open(match_file, 'r') as f:
            history = json.load(f)
        
        if len(history) < 2:
            return None
        
        opening = history[0]['books']
        current = history[-1]['books']
        
        report = {
            'match_id': match_id,
            'opening_time': history[0]['timestamp'],
            'current_time': history[-1]['timestamp'],
            'hours_elapsed': len(history),
            'movements': {}
        }
        
        for book in opening.keys():
            report['movements'][book] = self.calculate_line_movement(
                opening[book]['home'],
                current[book]['home']
            )
        
        # Detect consensus movement
        avg_movement = sum(m['change'] for m in report['movements'].values()) / len(report['movements'])
        report['consensus_movement'] = avg_movement
        report['sharp_signal'] = 'up' if avg_movement > 0.02 else ('down' if avg_movement < -0.02 else 'stable')
        
        return report

# Test instantiation
tracker = LineMovementTracker()
print("✅ LineMovementTracker class ready")
print("   Methods:")
print("   - fetch_current_odds() - Get odds from sportsbooks")
print("   - calculate_line_movement() - Track odds changes")
print("   - detect_sharp_money() - Find >5% movements")
print("   - log_match_odds() - Store historical odds")
print("   - get_line_movement_report() - Generate reports")
