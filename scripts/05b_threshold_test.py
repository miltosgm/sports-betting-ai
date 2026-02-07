#!/usr/bin/env python3
"""
Test different confidence thresholds to find optimal
"""

import pandas as pd
import numpy as np
import pickle
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backtest engine using importlib
import importlib.util
spec = importlib.util.spec_from_file_location("backtest", "scripts/05_backtest.py")
backtest_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backtest_module)
BacktestEngine = backtest_module.BacktestEngine

def test_all_thresholds():
    """Test multiple confidence thresholds"""
    
    print("🔍 Testing Different Confidence Thresholds")
    print("=" * 70)
    
    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
    
    results_summary = []
    
    for threshold in thresholds:
        # Create backtester with this threshold
        backtester = BacktestEngine('models/ensemble_model.pkl')
        backtester.confidence_threshold = threshold
        
        # Generate games
        games = backtester.generate_backtest_games()[:100]
        backtester.games_tested = len(games)
        
        # Run backtest
        for game in games:
            pred_result = backtester.predict_game(game['home'], game['away'], game['vegas_line'])
            
            if not pred_result['pass_filter']:
                continue
            
            backtester.bets_placed += 1
            
            actual_result = game['result']
            is_correct = False
            if pred_result['prediction'] == 'Home Win' and actual_result == 'Home Win':
                is_correct = True
            elif pred_result['prediction'] == 'Away/Draw' and actual_result != 'Home Win':
                is_correct = True
            
            bet_size = 150
            if is_correct:
                profit = bet_size
                backtester.wins += 1
            else:
                profit = -bet_size
                backtester.losses += 1
            
            backtester.total_pl += profit
        
        # Calculate metrics
        win_rate = (backtester.wins / backtester.bets_placed * 100) if backtester.bets_placed > 0 else 0
        roi = (backtester.total_pl / (backtester.bets_placed * 150)) * 100 if backtester.bets_placed > 0 else 0
        
        results_summary.append({
            'threshold': threshold,
            'bets': backtester.bets_placed,
            'wins': backtester.wins,
            'losses': backtester.losses,
            'win_rate': win_rate,
            'total_pl': backtester.total_pl,
            'roi': roi
        })
        
        print(f"\nThreshold: {threshold*100:.0f}%")
        print(f"  Bets: {backtester.bets_placed} | Win Rate: {win_rate:.1f}% | P&L: ${backtester.total_pl:+.0f} | ROI: {roi:+.1f}%")
    
    # Find best threshold
    print("\n" + "=" * 70)
    print("📊 SUMMARY - All Thresholds:")
    print("=" * 70)
    print(f"{'Threshold':<12} {'Bets':<8} {'Win%':<10} {'P&L':<12} {'ROI':<8}")
    print("-" * 70)
    
    for result in results_summary:
        print(f"{result['threshold']*100:>5.0f}%       {result['bets']:<8} {result['win_rate']:>6.1f}%    ${result['total_pl']:>8.0f}     {result['roi']:>6.1f}%")
    
    # Find best
    best = max(results_summary, key=lambda x: x['roi'])
    worst = min(results_summary, key=lambda x: x['roi'])
    
    print("\n" + "=" * 70)
    print(f"🏆 BEST:  {best['threshold']*100:.0f}% threshold - {best['win_rate']:.1f}% win rate, ${best['total_pl']:+.0f} P&L")
    print(f"❌ WORST: {worst['threshold']*100:.0f}% threshold - {worst['win_rate']:.1f}% win rate, ${worst['total_pl']:+.0f} P&L")
    
    if best['total_pl'] >= 0:
        print(f"\n✅ RECOMMENDATION: Use {best['threshold']*100:.0f}% threshold - PROFITABLE")
    else:
        print(f"\n❌ RECOMMENDATION: Model is unprofitable at all thresholds - NEEDS IMPROVEMENT")
    
    return results_summary

if __name__ == '__main__':
    results = test_all_thresholds()
