#!/usr/bin/env python3
"""
Results Tracker for Kick Lab AI
Fetches match results, updates predictions, calculates P/L
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import requests

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
PREDICTIONS_DIR = BASE_DIR / "data" / "predictions"
RESULTS_DIR = BASE_DIR / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class ResultsFetcher:
    """Fetches match results from various APIs"""
    
    def fetch_from_football_data_org(self, date):
        """
        Fetch results from football-data.org
        """
        try:
            url = "https://api.football-data.org/v4/competitions/PL/matches"
            
            params = {
                'dateFrom': date,
                'dateTo': date,
                'status': 'FINISHED'
            }
            
            headers = {
                'X-Auth-Token': os.getenv('FOOTBALL_DATA_API_KEY', '')
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for match in data.get('matches', []):
                    result = {
                        'home_team': match['homeTeam']['name'],
                        'away_team': match['awayTeam']['name'],
                        'home_score': match['score']['fullTime']['home'],
                        'away_score': match['score']['fullTime']['away'],
                        'date': match['utcDate'][:10],
                        'match_id': f"{match['homeTeam']['name']}-{match['awayTeam']['name']}-{match['utcDate'][:10]}".lower().replace(' ', '-')
                    }
                    
                    # Determine winner
                    if result['home_score'] > result['away_score']:
                        result['winner'] = 'Home Win'
                    elif result['away_score'] > result['home_score']:
                        result['winner'] = 'Away Win'
                    else:
                        result['winner'] = 'Draw'
                    
                    results.append(result)
                
                logger.info(f"✅ Fetched {len(results)} results from football-data.org")
                return results
            else:
                logger.warning(f"football-data.org returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching results: {e}")
            return []
    
    def fetch_from_api_football(self, date):
        """
        Fetch results from API-Football
        """
        try:
            url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
            
            headers = {
                'X-RapidAPI-Key': os.getenv('RAPID_API_KEY', ''),
                'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
            }
            
            params = {
                'league': '39',  # Premier League
                'season': '2025',
                'date': date,
                'status': 'FT'  # Full Time
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for match in data.get('response', []):
                    home_score = match['goals']['home']
                    away_score = match['goals']['away']
                    
                    result = {
                        'home_team': match['teams']['home']['name'],
                        'away_team': match['teams']['away']['name'],
                        'home_score': home_score,
                        'away_score': away_score,
                        'date': match['fixture']['date'][:10],
                        'match_id': f"{match['teams']['home']['name']}-{match['teams']['away']['name']}-{match['fixture']['date'][:10]}".lower().replace(' ', '-')
                    }
                    
                    # Determine winner
                    if home_score > away_score:
                        result['winner'] = 'Home Win'
                    elif away_score > home_score:
                        result['winner'] = 'Away Win'
                    else:
                        result['winner'] = 'Draw'
                    
                    results.append(result)
                
                logger.info(f"✅ Fetched {len(results)} results from API-Football")
                return results
            else:
                logger.warning(f"API-Football returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching results: {e}")
            return []
    
    def get_results(self, date):
        """
        Fetch results for a specific date
        Try multiple sources
        """
        logger.info(f"Fetching results for {date}...")
        
        # Try football-data.org
        results = self.fetch_from_football_data_org(date)
        if results:
            return results
        
        # Try API-Football
        results = self.fetch_from_api_football(date)
        if results:
            return results
        
        logger.warning(f"⚠️ No results found for {date}")
        return []


class ResultsTracker:
    """Tracks predictions vs actual results and calculates P/L"""
    
    def __init__(self):
        self.results_fetcher = ResultsFetcher()
    
    def load_predictions(self, date):
        """Load predictions for a specific date"""
        pred_file = PREDICTIONS_DIR / f"{date}_predictions.json"
        
        if not pred_file.exists():
            logger.warning(f"⚠️ No predictions found for {date}")
            return None
        
        with open(pred_file, 'r') as f:
            data = json.load(f)
        
        logger.info(f"📁 Loaded {len(data['predictions'])} predictions for {date}")
        return data
    
    def match_predictions_with_results(self, predictions_data, results):
        """Match predictions with actual results"""
        if not predictions_data or not results:
            return []
        
        predictions = predictions_data['predictions']
        matched = []
        
        for pred in predictions:
            # Try to find matching result
            match_result = None
            
            for result in results:
                # Match by teams (flexible matching)
                if (self._teams_match(pred['home_team'], result['home_team']) and
                    self._teams_match(pred['away_team'], result['away_team'])):
                    match_result = result
                    break
            
            if match_result:
                # Calculate accuracy
                correct = pred['prediction'] == match_result['winner']
                
                # Calculate P/L (simplified Kelly criterion betting)
                # Assume 1.5% bankroll bet on high-confidence picks
                bankroll = 10000  # Default bankroll
                bet_size = bankroll * 0.015
                
                if correct:
                    # Win: bet_size * odds
                    # Use suggested odds from prediction
                    if pred['prediction'] == 'Home Win':
                        odds = pred['suggested_odds']['home']
                    elif pred['prediction'] == 'Away Win':
                        odds = pred['suggested_odds']['away']
                    else:
                        odds = pred['suggested_odds']['draw']
                    
                    profit = bet_size * (odds - 1)
                else:
                    # Loss: -bet_size
                    profit = -bet_size
                
                matched_item = {
                    'match_id': pred['match_id'],
                    'home_team': pred['home_team'],
                    'away_team': pred['away_team'],
                    'date': pred['date'],
                    'predicted': pred['prediction'],
                    'actual': match_result['winner'],
                    'correct': correct,
                    'confidence': pred['confidence'],
                    'home_score': match_result['home_score'],
                    'away_score': match_result['away_score'],
                    'bet_size': round(bet_size, 2),
                    'profit_loss': round(profit, 2),
                    'odds_used': odds if correct else 0
                }
                
                matched.append(matched_item)
                
                status = "✅ CORRECT" if correct else "❌ INCORRECT"
                pl_sign = "+" if profit > 0 else ""
                logger.info(f"  {status}: {pred['home_team']} vs {pred['away_team']} | P/L: {pl_sign}${profit:.2f}")
        
        return matched
    
    def _teams_match(self, team1, team2):
        """Flexible team name matching"""
        # Normalize team names
        t1 = team1.lower().replace(' ', '').replace('-', '')
        t2 = team2.lower().replace(' ', '').replace('-', '')
        
        # Check if one contains the other (handles variations like "Man City" vs "Manchester City")
        return t1 in t2 or t2 in t1 or t1 == t2
    
    def calculate_summary(self, matched_results):
        """Calculate performance summary"""
        if not matched_results:
            return {
                'total_bets': 0,
                'correct': 0,
                'incorrect': 0,
                'accuracy': 0.0,
                'total_profit_loss': 0.0,
                'roi_percent': 0.0,
                'avg_confidence': 0.0
            }
        
        total = len(matched_results)
        correct = sum(1 for r in matched_results if r['correct'])
        incorrect = total - correct
        accuracy = (correct / total * 100) if total > 0 else 0
        
        total_pl = sum(r['profit_loss'] for r in matched_results)
        total_wagered = sum(r['bet_size'] for r in matched_results)
        roi = (total_pl / total_wagered * 100) if total_wagered > 0 else 0
        
        avg_confidence = sum(r['confidence'] for r in matched_results) / total if total > 0 else 0
        
        return {
            'total_bets': total,
            'correct': correct,
            'incorrect': incorrect,
            'accuracy': round(accuracy, 2),
            'total_profit_loss': round(total_pl, 2),
            'total_wagered': round(total_wagered, 2),
            'roi_percent': round(roi, 2),
            'avg_confidence': round(avg_confidence, 4)
        }
    
    def save_results(self, date, matched_results, summary):
        """Save results to JSON file"""
        output = {
            'date': date,
            'tracked_at': datetime.now().isoformat(),
            'summary': summary,
            'results': matched_results
        }
        
        output_file = RESULTS_DIR / f"{date}_results.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"💾 Saved results to {output_file}")
        return output_file
    
    def update_database(self, matched_results):
        """Update prediction records in database with actual results"""
        try:
            from backend.app import db, Prediction
            
            for result in matched_results:
                pred = Prediction.query.filter_by(match_id=result['match_id']).first()
                
                if pred:
                    pred.actual_result = result['actual']
                    pred.result_timestamp = datetime.now()
                    logger.info(f"  ✅ Updated database for {result['match_id']}")
            
            db.session.commit()
            logger.info("✅ Database updated with results")
            
        except ImportError:
            logger.warning("⚠️ Database module not available, skipping DB update")
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
    
    def track_date(self, date):
        """
        Track results for a specific date
        Main entry point
        """
        logger.info("=" * 60)
        logger.info(f"📊 RESULTS TRACKING FOR {date}")
        logger.info("=" * 60)
        
        # Load predictions
        predictions_data = self.load_predictions(date)
        if not predictions_data:
            logger.warning("⚠️ No predictions to track")
            return None
        
        # Fetch results
        results = self.results_fetcher.get_results(date)
        if not results:
            logger.warning("⚠️ No results available yet")
            return None
        
        # Match predictions with results
        matched = self.match_predictions_with_results(predictions_data, results)
        
        # Calculate summary
        summary = self.calculate_summary(matched)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Total Bets: {summary['total_bets']}")
        print(f"Correct: {summary['correct']} ✅")
        print(f"Incorrect: {summary['incorrect']} ❌")
        print(f"Accuracy: {summary['accuracy']}%")
        print(f"Total P/L: ${summary['total_profit_loss']:+.2f}")
        print(f"Total Wagered: ${summary['total_wagered']:.2f}")
        print(f"ROI: {summary['roi_percent']:+.2f}%")
        print(f"Avg Confidence: {summary['avg_confidence']*100:.1f}%")
        print("=" * 60)
        
        # Save results
        self.save_results(date, matched, summary)
        
        # Update database
        try:
            self.update_database(matched)
        except Exception as e:
            logger.warning(f"⚠️ Could not update database: {e}")
        
        logger.info("=" * 60)
        logger.info("✅ RESULTS TRACKING COMPLETE")
        logger.info("=" * 60)
        
        return {
            'summary': summary,
            'matched_results': matched
        }


def main():
    """Track results for yesterday"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    tracker = ResultsTracker()
    results = tracker.track_date(yesterday)
    
    if results:
        return results
    else:
        logger.info("ℹ️ No results to track for yesterday")
        return None


if __name__ == '__main__':
    main()
