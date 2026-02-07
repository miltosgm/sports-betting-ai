#!/usr/bin/env python3
"""
Phase 5b: Track Daily Results
Monitor actual game results and calculate P&L
"""

import pandas as pd
import json
from datetime import datetime
import os

class ResultsTracker:
    def __init__(self):
        self.results_file = 'results/daily_results.json'
        self.tracking_file = 'results/profit_tracking.json'
        os.makedirs('results', exist_ok=True)
    
    def log_result(self, game_name, prediction, actual_result, bet_size, edge):
        """
        Log a game result
        
        Args:
            game_name: "Arsenal vs Liverpool"
            prediction: "Home Win"
            actual_result: "Home Win" / "Draw" / "Away Win"
            bet_size: $150
            edge: +2.1%
        """
        is_win = prediction == actual_result
        profit = bet_size if is_win else -bet_size
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'game': game_name,
            'prediction': prediction,
            'actual': actual_result,
            'result': '✅ WIN' if is_win else '❌ LOSS',
            'bet_size': bet_size,
            'profit_loss': profit,
            'edge': edge
        }
        
        # Append to results file
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r') as f:
                results = json.load(f)
        else:
            results = []
        
        results.append(result)
        
        with open(self.results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return result
    
    def calculate_daily_pl(self):
        """Calculate today's profit/loss"""
        if not os.path.exists(self.results_file):
            return 0, []
        
        with open(self.results_file, 'r') as f:
            results = json.load(f)
        
        today = datetime.now().strftime('%Y-%m-%d')
        today_results = [r for r in results if r['timestamp'].startswith(today)]
        
        total_pl = sum(r['profit_loss'] for r in today_results)
        wins = len([r for r in today_results if r['result'] == '✅ WIN'])
        losses = len([r for r in today_results if r['result'] == '❌ LOSS'])
        
        return total_pl, today_results, wins, losses
    
    def format_results_message(self):
        """Format results for Telegram"""
        total_pl, results, wins, losses = self.calculate_daily_pl()
        
        if not results:
            return "📊 No games completed yet today"
        
        msg = f"📊 TODAY'S RESULTS - {datetime.now().strftime('%b %d')}\n\n"
        
        for r in results:
            msg += f"{r['result']} {r['game']}\n"
            msg += f"   Predicted: {r['prediction']} | Actual: {r['actual']}\n"
            msg += f"   P&L: ${r['profit_loss']}\n\n"
        
        msg += "=" * 40 + "\n"
        msg += f"Record: {wins}W - {losses}L\n"
        msg += f"Daily P&L: ${total_pl:+.2f}\n"
        
        if total_pl > 0:
            msg += f"🟢 PROFIT\n"
        elif total_pl < 0:
            msg += f"🔴 LOSS\n"
        else:
            msg += f"⚪ BREAK EVEN\n"
        
        return msg
    
    def update_tracking(self):
        """Update long-term tracking"""
        if not os.path.exists(self.results_file):
            return
        
        with open(self.results_file, 'r') as f:
            all_results = json.load(f)
        
        # Calculate cumulative stats
        total_bets = len(all_results)
        wins = len([r for r in all_results if r['result'] == '✅ WIN'])
        losses = total_bets - wins
        win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
        total_profit = sum(r['profit_loss'] for r in all_results)
        
        tracking = {
            'last_updated': datetime.now().isoformat(),
            'total_bets': total_bets,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 1),
            'total_profit': round(total_profit, 2),
            'avg_bet': round(sum(r['bet_size'] for r in all_results) / total_bets, 2) if total_bets > 0 else 0,
            'roi': round(total_profit / (sum(r['bet_size'] for r in all_results)) * 100, 2) if total_bets > 0 else 0
        }
        
        with open(self.tracking_file, 'w') as f:
            json.dump(tracking, f, indent=2)
        
        return tracking

def main():
    print("📊 Phase 5b: Results Tracking")
    print("=" * 50)
    
    tracker = ResultsTracker()
    
    # Show results message
    msg = tracker.format_results_message()
    print(msg)
    
    # Update tracking
    stats = tracker.update_tracking()
    if stats:
        print("\n📈 OVERALL STATS")
        print(f"Total Bets: {stats['total_bets']}")
        print(f"Win Rate: {stats['win_rate']}%")
        print(f"Total Profit: ${stats['total_profit']}")
        print(f"ROI: {stats['roi']}%")

if __name__ == '__main__':
    main()
