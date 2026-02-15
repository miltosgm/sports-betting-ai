#!/usr/bin/env python3
"""
Diagnostic Backtest Script
Identify WHY the model failed on Feb 7, 2026

Tests:
1. Is 75% accuracy real on 2024-only games?
2. What's actual home advantage weight?
3. Is travel distance feature important?
4. What's realistic live accuracy?
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

print("🔍 DIAGNOSTIC BACKTEST - Feb 7 Failure Analysis")
print("=" * 80)

# Load the V5 model
model_path = Path("models/ensemble_model_v5_proper.pkl")
if not model_path.exists():
    print(f"❌ Model not found: {model_path}")
    exit(1)

with open(model_path, 'rb') as f:
    ensemble = pickle.load(f)

print("✓ Model loaded")
print(f"  Test accuracy (training): {ensemble['accuracy']['test_mean']:.1%}")
print()

# Load data
try:
    data_file = Path("data/processed/features_engineered_v2.csv")
    df = pd.read_csv(data_file)
    print(f"✓ Data loaded: {len(df)} games")
except:
    print("❌ Data file not found")
    exit(1)

# Create home_win if missing
if 'home_win' not in df.columns:
    df['home_win'] = (df['home_goals'] > df['away_goals']).astype(int)

# Prepare features
feature_cols = [c for c in df.columns if c not in 
               ['game_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score', 'home_win']]
feature_cols = [c for c in feature_cols if c in df.columns]

X = df[feature_cols].fillna(0)
y = df['home_win'].astype(int)

print()
print("=" * 80)
print("TEST 1: Accuracy on 2024 Games Only")
print("=" * 80)

# Try to split by year if date column exists
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year
    
    recent_data = df[df['year'] >= 2024]
    if len(recent_data) > 50:
        X_recent = recent_data[feature_cols].fillna(0)
        y_recent = recent_data['home_win'].astype(int)
        
        X_train_recent, X_test_recent, y_train_recent, y_test_recent = train_test_split(
            X_recent, y_recent, test_size=0.3, random_state=42
        )
        
        scaler = StandardScaler()
        X_test_recent_scaled = scaler.fit_transform(X_train_recent)
        X_test_recent_scaled = scaler.transform(X_test_recent)
        
        try:
            # Get predictions
            probs = []
            for model_name, model in ensemble['models'].items():
                try:
                    prob = model.predict_proba(X_test_recent_scaled)[:, 1]
                    probs.append(prob * ensemble['weights'][model_name])
                except:
                    pass
            
            ensemble_pred = np.mean(probs, axis=0)
            acc_recent = (ensemble_pred.round() == y_test_recent).mean()
            
            print(f"✓ 2024-only games test:")
            print(f"  Sample size: {len(X_recent)} games")
            print(f"  Accuracy: {acc_recent:.1%}")
            
            if acc_recent < 0.60:
                print(f"  ⚠️  LOWER than training (75%)")
                print(f"  Likely cause: Model is overfit to 2014-2023 patterns")
            
        except Exception as e:
            print(f"  Error calculating accuracy: {e}")
    else:
        print("  ⚠️  Not enough 2024 games in dataset")
else:
    print("  ⚠️  No date column, cannot test by year")

print()
print("=" * 80)
print("TEST 2: Feature Analysis - What's Important?")
print("=" * 80)

# Check for key features
key_features = {
    'travel': [c for c in feature_cols if 'travel' in c.lower()],
    'home': [c for c in feature_cols if 'home' in c.lower()],
    'away': [c for c in feature_cols if 'away' in c.lower()],
    'form': [c for c in feature_cols if 'form' in c.lower()],
    'injury': [c for c in feature_cols if 'injury' in c.lower()],
}

print("Features by category:")
for category, features in key_features.items():
    if features:
        print(f"  {category}: {features}")

# Try feature importance from XGBoost
try:
    if hasattr(ensemble['models']['xgboost'], 'feature_importances_'):
        importances = ensemble['models']['xgboost'].feature_importances_
        feature_importance = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
        
        print(f"\nTop 10 important features (XGBoost):")
        for i, (feat, imp) in enumerate(feature_importance[:10], 1):
            print(f"  {i}. {feat}: {imp:.4f}")
        
        # Check if travel is really #1
        travel_features_imp = [imp for feat, imp in feature_importance if 'travel' in feat.lower()]
        if travel_features_imp:
            travel_rank = [i for i, (feat, imp) in enumerate(feature_importance) if 'travel' in feat.lower()]
            if travel_rank:
                print(f"\n  ℹ️  Travel features ranked: {[t+1 for t in travel_rank[:3]]}")
                if travel_rank[0] > 5:
                    print(f"  ⚠️  Travel distance is NOT #1 feature (rank #{travel_rank[0]+1})")
        
except Exception as e:
    print(f"  Could not get feature importance: {e}")

print()
print("=" * 80)
print("TEST 3: Home Advantage Calibration")
print("=" * 80)

# Compare home vs away accuracy
try:
    X_scaled = scaler.fit_transform(X)
    
    # Get ensemble predictions
    probs = []
    for model_name, model in ensemble['models'].items():
        try:
            prob = model.predict_proba(X_scaled)[:, 1]
            probs.append(prob * ensemble['weights'][model_name])
        except:
            pass
    
    ensemble_pred = np.mean(probs, axis=0)
    
    # Analyze by PPG difference (proxy for team quality)
    if 'home_ppg' in feature_cols and 'away_ppg' in feature_cols:
        home_ppg = df['home_ppg'].values
        away_ppg = df['away_ppg'].values
        ppg_diff = home_ppg - away_ppg
        
        # Groups: Home strong favorite, balanced, home underdog
        strong_fav = ppg_diff > 0.3  # Home much better
        balanced = (ppg_diff >= -0.3) & (ppg_diff <= 0.3)
        underdog = ppg_diff < -0.3  # Home worse
        
        print("Accuracy by team quality gap:")
        
        if strong_fav.sum() > 0:
            acc_fav = (ensemble_pred[strong_fav].round() == y[strong_fav]).mean()
            print(f"  Home strong favorite (PPG +0.3+): {acc_fav:.1%} ({strong_fav.sum()} games)")
        
        if balanced.sum() > 0:
            acc_bal = (ensemble_pred[balanced].round() == y[balanced]).mean()
            print(f"  Balanced (PPG -0.3 to +0.3): {acc_bal:.1%} ({balanced.sum()} games)")
        
        if underdog.sum() > 0:
            acc_under = (ensemble_pred[underdog].round() == y[underdog]).mean()
            print(f"  Home underdog (PPG -0.3-): {acc_under:.1%} ({underdog.sum()} games)")
            
            if acc_under > acc_fav:
                print(f"\n  ⚠️  Home advantage is TOO HIGH")
                print(f"     Model predicts underdog home teams better than favorites")
                print(f"     Suggests home advantage weight > team quality weight")

except Exception as e:
    print(f"  Error: {e}")

print()
print("=" * 80)
print("TEST 4: Model Confidence Calibration")
print("=" * 80)

print("\nChecking if model confidence matches actual accuracy:")

# Get confidence levels
try:
    confidence_bins = [0.5, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    
    for threshold in confidence_bins:
        conf_mask = ensemble_pred >= threshold
        if conf_mask.sum() > 10:
            acc = (ensemble_pred[conf_mask].round() == y[conf_mask]).mean()
            count = conf_mask.sum()
            print(f"  Confidence {threshold:.0%}+: {acc:.1%} accuracy ({count} games)")
            
            if acc < threshold:
                gap = threshold - acc
                print(f"           ⚠️  Model overconfident by {gap:.1%}")

except Exception as e:
    print(f"  Error: {e}")

print()
print("=" * 80)
print("SUMMARY & DIAGNOSIS")
print("=" * 80)

print("""
Likely Causes of Feb 7 Failure (0/3 bets lost):

1. ❌ OVERFITTING to 2014-2023 data
   - 75% accuracy on training data
   - 0% on Feb 7 live games = huge gap
   - Model learned noise, not signal

2. ❌ HOME ADVANTAGE OVERWEIGHTED
   - Model: "Home + Travel = 75% win"
   - Reality: Team quality >> home advantage
   - Wolves (bottom) at home vs Chelsea (top) away
   - Model missed: Chelsea is 4x better

3. ❌ TRAVEL DISTANCE FEATURE QUESTIONABLE
   - Your #1 edge factor might be noise
   - 0/3 suggests it's not reliable
   - Need to validate if real or artifact

4. ❌ INSUFFICIENT RECENT DATA
   - Only 2,660 games total
   - Patterns from 2014-2019 might not apply 2026
   - Need to test on 2024+ only

NEXT STEPS:
1. Run test 1 above - does 75% hold on 2024 games?
2. Review feature importance - is travel really top?
3. Recalibrate home advantage weight
4. Accept 55-60% as realistic accuracy
5. Paper trade for 4 full weeks before any real money
""")

print("=" * 80)
print("Report complete. Check results above.")
