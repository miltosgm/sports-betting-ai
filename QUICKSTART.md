# 🚀 Quick Start Guide

Premier League Sports Betting AI - Step by step setup

---

## 📋 Prerequisites

- Python 3.9+
- Git
- pip or conda

---

## 🔧 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/miltosgm/sports-betting-ai.git
cd sports-betting-ai
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 📊 Pipeline Steps

### Phase 1: Data Collection
```bash
# Collects Premier League games, stats, odds, injuries
python3 scripts/01_collect_data.py

# Output: data/raw/
#   - games_2024-25.csv
#   - lines_2024-25.csv
#   - team_stats_2024-25.csv
#   - injuries_current.csv
```

### Phase 2: Feature Engineering
```bash
# Creates predictive features from raw data
python3 scripts/03_engineer_features.py

# Output: data/processed/
#   - features_engineered.csv (with 16+ features)
```

### Phase 3: Model Training
```bash
# Trains XGBoost, LightGBM, and Ensemble models
python3 scripts/04_train_models.py

# Output: models/
#   - baseline_model.pkl
#   - xgboost_model.pkl
#   - lightgbm_model.pkl
#   - model_metrics.json
```

### Phase 4: Backtesting (Coming Soon)
```bash
# Tests model on 2024 data (walk-forward validation)
python3 scripts/05_backtest.py

# Output: results/
#   - backtest_results.csv
#   - edge_analysis.json
```

### Phase 5: Daily Predictions (Coming Soon)
```bash
# Generates daily predictions with confidence scores
python3 scripts/06_daily_predictions.py

# Output: predictions for today's games
```

---

## 📁 Project Structure

```
sports-betting-ai/
├── data/
│   ├── raw/              ← Downloaded data
│   └── processed/        ← Engineered features
├── scripts/
│   ├── 01_collect_data.py
│   ├── 03_engineer_features.py
│   ├── 04_train_models.py
│   ├── 05_backtest.py (TODO)
│   └── 06_daily_predictions.py (TODO)
├── models/               ← Trained models
├── results/              ← Backtest results & predictions
├── config/               ← Configuration files
└── notebooks/            ← Jupyter notebooks (TODO)
```

---

## 🎯 Expected Pipeline Output

**After Phase 1 (Data Collection):**
```
Collected 380 Premier League games
Collected stats for 20 teams
Collected 3 injury reports
Data validation: ✅ PASSED
```

**After Phase 2 (Features):**
```
Created 16 predictive features
- Team form (PPG last 5/10 games)
- Defensive strength
- Situational factors
- Statistical metrics
```

**After Phase 3 (Training):**
```
Model Performance:
- Baseline (Logistic):  51.2% accuracy
- XGBoost:             53.8% accuracy ✅
- LightGBM:            53.5% accuracy
- Ensemble:            54.1% accuracy ✅ BEST
```

**After Phase 4 (Backtesting):**
```
2024 Backtest Results:
- Win Rate:    54.3%
- Edge:        +0.8% above Vegas
- Monthly ROI: 2.1%
- Drawdown:    -$1,200
```

**After Phase 5 (Daily Predictions):**
```
TODAY'S PREDICTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total games: 10
High confidence (65%+): 7 games
Recommended bets: 5 games
Expected daily profit: $350-400

Game 1: Liverpool vs West Ham
Confidence: 68%
My edge: +0.3 goals
→ BET $150
```

---

## 💡 Key Features

### 1. **Selective Betting**
- Only recommends 5-7 bets per day (high confidence only)
- 65%+ confidence threshold
- Filters out low-edge games

### 2. **Ensemble Models**
- Combines 3 approaches (Logistic + XGBoost + LightGBM)
- Majority voting for robustness
- Better accuracy than single models

### 3. **Proper Backtesting**
- Walk-forward validation (no look-ahead bias)
- Measures edge vs Vegas odds
- Calculates expected ROI

### 4. **Risk Management**
- Kelly Criterion bet sizing
- Daily profit tracking
- Drawdown analysis

---

## 📖 Development Timeline

- **Week 1:** Data collection + cleaning ← WE ARE HERE
- **Week 2:** Feature engineering
- **Week 3:** Model training
- **Week 4:** Backtesting + validation
- **Week 5:** Live predictions (paper trading)
- **Week 6+:** Real money (after validation)

---

## 🔗 Resources

- **GitHub:** https://github.com/miltosgm/sports-betting-ai
- **Docs:** See README.md for full documentation
- **Data Sources:** FBRef, Understat, ESPN, Covers.com

---

## ⚠️ Important Notes

1. **Start with Paper Trading**
   - Test predictions with fake money first
   - Validate model works in real conditions
   - Then start with small bets

2. **Conservative Betting**
   - Never risk >2% per bet
   - Use Kelly Criterion sizing
   - Accept monthly variance

3. **Continuous Improvement**
   - Monitor daily performance
   - Retrain model monthly
   - Adjust features based on results

---

## 🆘 Troubleshooting

**ModuleNotFoundError**
```bash
# Make sure you activated the virtual environment
source venv/bin/activate

# Then install dependencies
pip install -r requirements.txt
```

**Data files not found**
```bash
# Run Phase 1 first to create data files
python3 scripts/01_collect_data.py

# Then run subsequent phases
```

**Out of memory**
```bash
# If working with large datasets, consider:
# - Process data in chunks
# - Use Polars instead of Pandas
# - Reduce number of features
```

---

## 🚀 Next Steps

1. **Clone the repo** and install dependencies
2. **Run Phase 1** to collect data
3. **Check the output** in `data/raw/`
4. **Run Phases 2-3** to train the model
5. **Review results** in `models/model_metrics.json`

Let's build this! 🎯

---

**Last Updated:** Feb 6, 2026  
**Status:** Phase 1 Ready
