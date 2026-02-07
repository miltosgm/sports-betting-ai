# Sports Betting AI v2 - Deployment Guide

## 🚀 Quick Start

### Load Improved Model:
```python
import pickle
import numpy as np

# Load the improved ensemble
with open('models/ensemble_model_v2.pkl', 'rb') as f:
    ensemble = pickle.load(f)

# Access components
models = ensemble['models']           # Dict of 3 models
weights = ensemble['weights']         # Weighted voting dict
scaler = ensemble['scaler']           # Feature scaler
feature_names = ensemble['feature_names']  # 39 feature names
```

### Make a Prediction:
```python
import pandas as pd

# Get game features (30 features minimum)
features = np.array([[...30 features...]])

# Scale features
features_scaled = scaler.transform(features)

# Get weighted ensemble prediction
xgb_proba = models['xgboost'].predict_proba(features_scaled)[0, 1]
lgb_proba = models['lightgbm'].predict_proba(features_scaled)[0, 1]
rf_proba = models['random_forest'].predict_proba(features_scaled)[0, 1]

# Weighted ensemble
ensemble_proba = (
    xgb_proba * weights['xgboost'] +
    lgb_proba * weights['lightgbm'] +
    rf_proba * weights['random_forest']
)

# Decision
prediction = "Home Win" if ensemble_proba > 0.5 else "Away/Draw"
confidence = ensemble_proba if ensemble_proba > 0.5 else 1 - ensemble_proba

if confidence >= 0.65:
    print(f"BET: {prediction} (confidence: {confidence*100:.1f}%)")
else:
    print(f"PASS: Confidence too low ({confidence*100:.1f}%)")
```

---

## 📊 Model Performance Summary

### Individual Models (Test Set):
| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| XGBoost | 76.47% | 75.86% | 66.67% | 70.97% | 0.859 |
| LightGBM | 77.78% | 77.59% | 68.18% | 72.58% | 0.851 |
| RandomForest | 72.55% | 69.35% | 65.15% | 67.19% | 0.817 |
| **Ensemble** | **77.12%** | **78.18%** | **65.15%** | **71.07%** | **~0.85** |

### Ensemble Weights:
- **LightGBM:** 34.29% (most accurate)
- **XGBoost:** 33.72%
- **RandomForest:** 31.99%

---

## 🎯 Feature Set (30 Features)

### Form Features (8):
```python
features = {
    'home_ppg_last_3': float,
    'home_ppg_last_5': float,
    'home_ppg_last_10': float,
    'home_momentum': float,  # NEW: Recency-weighted
    'away_ppg_last_3': float,
    'away_ppg_last_5': float,
    'away_ppg_last_10': float,
    'away_momentum': float,  # NEW: Recency-weighted
}
```

### Defensive Features (6):
```python
{
    'home_def_last_3': float,
    'home_def_last_5': float,
    'home_goal_diff': float,  # NEW: Offensive - Defensive
    'away_def_last_3': float,
    'away_def_last_5': float,
    'away_goal_diff': float,  # NEW: Offensive - Defensive
}
```

### Home/Away Splits (3):
```python
{
    'home_ppg_home_last_5': float,    # NEW
    'away_ppg_away_last_5': float,    # NEW
    'home_win_rate': float,            # NEW
}
```

### Head-to-Head (1):
```python
{
    'h2h_home_win_rate': float,  # NEW: Last 5 matchups
}
```

### Travel Fatigue (4):
```python
{
    'home_rest_days': float,           # NEW: Days since last match
    'away_rest_days': float,           # NEW: Days since last match
    'away_travel_fatigue': float,      # NEW: Distance / Rest
    'home_travel_advantage': float,    # NEW: Inverse of away fatigue
}
```

### Weather/Environmental (1):
```python
{
    'weather_home_advantage_modifier': float,  # NEW: +0.15 in bad weather
}
```

### Referee Bias (2):
```python
{
    'ref_home_bias_history': float,        # NEW: Historical pattern
    'ref_bias_adjusted_ppg': float,        # NEW: Adjusted performance
}
```

### Motivation (2):
```python
{
    'home_motivation': float,  # NEW: Derby + title race + relegation
    'away_motivation': float,  # NEW: Derby + title race + relegation
}
```

### Injuries (5):
```python
{
    'home_key_injuries': int,              # NEW: Number of key players out
    'away_key_injuries': int,              # NEW: Number of key players out
    'home_injury_impact': float,           # NEW: 10% reduction per player
    'away_injury_impact': float,           # NEW: 10% reduction per player
    'home_ppg_injury_adjusted': float,     # NEW: Form adjusted for injuries
    'away_ppg_injury_adjusted': float,     # NEW: Form adjusted for injuries
}
```

---

## 📈 Feature Importance (Top 20)

1. **travel_distance** (139) - Distance between stadiums
2. **ref_home_bias_history** (135) - Ref's historical home bias
3. **home_rest_days** (114) - Days rest for home team
4. **away_travel_fatigue** (103) - Long travel + short rest
5. **home_ppg_last_3** (103) - Recent home form
6. **ref_bias_adjusted_ppg** (102) - Performance adjusted for ref bias
7. **away_rest_days** (94) - Days rest for away team
8. **home_def_last_3** (89) - Recent home defense
9. **away_def_last_3** (89) - Recent away defense
10. **away_goal_diff** (85) - Away team goal differential

*See `models/feature_importance_v2.json` for complete ranking*

---

## 💰 Betting Strategy

### Confidence Threshold: 65%
- Only place bets when model ≥ 65% confident
- Reduces number of bets but improves quality
- ~35-40 bets per 100 games analyzed

### Expected Win Rate: 54-58%
- Baseline to be profitable at -110 odds
- Ensemble typically hits 55-57% in backtesting

### Position Sizing:
```
Conservative:  $150 per bet
Aggressive:    $250 per bet
Maximum:       Never risk >2% of bankroll per game
```

### Daily Management:
```
Max Loss per Day:  $500
Max Bets per Day:  5-7
Target Daily P&L:  +$200 to +$400
```

---

## 🔄 Integration Points

### With Betting APIs:
```python
# Get live odds
from pinnacle_api import get_live_odds

game = {
    'home_team': 'Manchester City',
    'away_team': 'Liverpool',
    'date': '2024-02-07'
}

# Get our prediction
features = engineer_features(game)  # 30 features
confidence = predict_with_ensemble(features)

# Get Vegas line
vegas_line = get_live_odds(game)

# Decide to bet
if confidence >= 0.65 and has_positive_edge(confidence, vegas_line):
    place_bet(game, amount=150)
```

### With Injury Database:
```python
# Update injury data (currently synthetic)
injuries = get_injuries_from_api()  # API call

# Adjust features
features['home_key_injuries'] = len(injuries['home_team_key_players'])
features['away_key_injuries'] = len(injuries['away_team_key_players'])

# Calculate injury impact
features['home_injury_impact'] = 1 - (features['home_key_injuries'] * 0.10)
features['away_injury_impact'] = 1 - (features['away_key_injuries'] * 0.10)
```

### With Weather Data:
```python
import requests

# Get weather for match location
weather = get_weather_api(location=game['home_team'])

# Adverse weather indicator
is_adverse = weather['wind_speed'] > 15 or weather['precipitation'] > 0.6

# Add to features
features['weather_home_advantage_modifier'] = 0.15 if is_adverse else 0.0
```

---

## 📋 Required Python Packages

```
numpy>=1.20
pandas>=1.3
scikit-learn>=0.24
xgboost>=1.5
lightgbm>=3.3
joblib>=1.0
```

Install:
```bash
pip install -r requirements.txt
```

---

## ✅ Validation Checklist

Before deploying to live betting:

- [ ] Load ensemble model successfully
- [ ] Test predictions on known games
- [ ] Verify feature scaling works
- [ ] Check confidence calibration (65%+ should win ~65% of time)
- [ ] Validate against historical results
- [ ] Run 2+ weeks paper trading
- [ ] Monitor daily accuracy
- [ ] Check for concept drift (retest weekly)
- [ ] Confirm odds availability
- [ ] Set up loss limits and alerts

---

## 🎯 Performance Monitoring

### Daily Tracking:
```python
results = {
    'date': '2024-02-07',
    'predictions': 6,
    'wins': 4,
    'losses': 2,
    'win_rate': 0.667,
    'pl': 300,
}

# Should maintain 54-58% win rate
# Losing streaks of 10+ are normal
# Monitor for model drift weekly
```

### Red Flags (Stop Trading):
- ❌ Win rate drops below 50% over 50+ games
- ❌ Same prediction wrong 10+ times in a row
- ❌ Confidence not correlating with accuracy
- ❌ Major injuries/news not captured

---

## 📊 Version Info

- **Version:** 2.0.0
- **Created:** February 7, 2026
- **Models:** XGBoost, LightGBM, RandomForest
- **Ensemble:** Weighted voting
- **Accuracy:** 77.12% (test set)
- **Status:** ✅ Ready for Paper Trading

---

## 🔗 Files Reference

```
models/
├── ensemble_model_v2.pkl          # Main deployment file
├── xgboost_model_v2.pkl           # Individual model
├── lightgbm_model_v2.pkl          # Individual model
├── random_forest_model_v2.pkl     # Individual model
├── scaler_v2.pkl                  # Feature scaling
├── model_metrics_v2.json          # Accuracy metrics
└── feature_importance_v2.json     # Feature rankings

data/processed/
└── features_engineered_v2.csv     # Training data (763 games)

scripts/
├── 03_engineer_features_v2.py     # Create 30 features
├── 04_train_models_v2.py          # Train ensemble
└── 05_backtest_v2.py              # Validate on 2024 data
```

---

For detailed information, see `PHASE_1-3_IMPROVEMENT_REPORT.md`
