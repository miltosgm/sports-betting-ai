# ⚽ Sports Betting AI - Premier League

Machine learning model for Premier League predictions with 5-7 selective bets per day at 65%+ confidence.

**Status:** 🚀 Phase 1 - Data Collection  
**Target:** 57-65% win rate  
**Expected Daily Profit:** $300-600  
**Bets Per Day:** 5-7 (high confidence only)

---

## 🎯 The Model

**What it does:**
1. Collects Premier League game data (teams, stats, odds)
2. Engineers predictive features (rolling averages, situational factors)
3. Trains ML ensemble (XGBoost + LightGBM)
4. Generates daily predictions with confidence scores
5. Identifies betting edges (where we beat Vegas)
6. Recommends only 65%+ confidence bets

**Output:** 5-7 daily predictions with edge analysis

---

## 📂 Project Structure

```
sports-betting-ai/
├── README.md                          (this file)
├── requirements.txt                   (Python dependencies)
├── .gitignore                         (git exclusions)
│
├── data/
│   ├── raw/                           (downloaded data)
│   │   ├── games_2023_2024.csv
│   │   ├── games_2024_2025.csv
│   │   ├── lines_historical.csv
│   │   ├── team_stats.csv
│   │   └── injuries_current.csv
│   │
│   └── processed/                     (engineered features)
│       ├── features_engineered.csv
│       └── train_test_split.csv
│
├── scripts/
│   ├── 01_collect_data.py             (data scraping)
│   ├── 02_clean_data.py               (data cleaning)
│   ├── 03_engineer_features.py        (feature creation)
│   ├── 04_train_models.py             (model training)
│   ├── 05_backtest.py                 (historical validation)
│   └── 06_daily_predictions.py        (live predictions)
│
├── notebooks/
│   ├── 01_EDA.ipynb                   (exploration)
│   ├── 02_Feature_Analysis.ipynb      (feature importance)
│   └── 03_Backtest_Results.ipynb      (performance analysis)
│
├── models/
│   ├── xgboost_model.pkl
│   ├── lightgbm_model.pkl
│   ├── ensemble_model.pkl
│   └── model_metrics.json
│
├── config/
│   ├── data_config.yaml               (data sources)
│   ├── feature_config.yaml            (feature definitions)
│   └── model_config.yaml              (hyperparameters)
│
└── results/
    ├── backtest_results.csv
    ├── daily_predictions.csv
    ├── profit_tracking.json
    └── edge_analysis.json
```

---

## 🚀 Quick Start

```bash
# 1. Clone repo
git clone https://github.com/miltosgm/sports-betting-ai.git
cd sports-betting-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp config/data_config.yaml.example config/data_config.yaml
# Edit with your preferences

# 4. Collect data
python scripts/01_collect_data.py --season 2024-25

# 5. Train model
python scripts/03_engineer_features.py
python scripts/04_train_models.py

# 6. Backtest
python scripts/05_backtest.py

# 7. Get predictions
python scripts/06_daily_predictions.py
```

---

## 📊 Current Phase: Data Collection

**What we're doing now:**
- Scraping Premier League game data (2023-2025)
- Collecting Vegas lines + results
- Getting team statistics
- Validating data quality

**Target:**
- ✅ 380 games/season × 2 seasons = 760 games
- ✅ 98%+ data completeness
- ✅ Verified against official sources

---

## 🎯 Success Metrics

**Phase 1 (Data):**
- [ ] Collect 760+ games
- [ ] 98%+ completeness
- [ ] Data validated

**Phase 2 (Features):**
- [ ] Create 30+ features
- [ ] Feature correlation analysis
- [ ] Non-correlated features removed

**Phase 3 (Model):**
- [ ] Baseline accuracy: 52%+
- [ ] Ensemble accuracy: 54%+
- [ ] Model stability across time

**Phase 4 (Backtest):**
- [ ] Win rate: 57%+
- [ ] Edge calculation: Positive EV
- [ ] Drawdown: < $2,000

**Phase 5 (Live):**
- [ ] Paper trading matches backtest
- [ ] Daily profit tracking
- [ ] Confidence vs accuracy validated

---

## 💰 Profit Projections

```
Conservative (5 bets/day, 57% win rate):
Daily:    $296
Weekly:   $1,480
Monthly:  $5,920
Annual:   $71,040

Target (7 bets/day, 60% win rate):
Daily:    $415
Weekly:   $2,075
Monthly:  $8,300
Annual:   $99,600

Optimistic (10 bets/day, 62% win rate):
Daily:    $592
Weekly:   $2,960
Monthly:  $11,860
Annual:   $142,320
```

---

## 🛠️ Tech Stack

- **Language:** Python 3.9+
- **Data:** Pandas, NumPy
- **ML:** XGBoost, LightGBM, Scikit-learn
- **Backtesting:** Walk-forward validation (custom)
- **Visualization:** Matplotlib, Plotly
- **APIs:** ESPN, SofaScore, betting APIs

---

## 📚 Data Sources

**Games & Stats:**
- FBRef (Sports Reference) - https://fbref.com
- Understat - https://understat.com
- ESPN API - https://www.espn.com
- Official Premier League - https://www.premierleague.com

**Betting Lines:**
- Covers.com - https://www.covers.com
- Pinnacle - https://www.pinnacle.com
- SBR Forum - https://www.sbrforum.com

**Injuries & Team News:**
- Sky Sports - https://www.skysports.com
- Official club websites
- Transfermarkt - https://www.transfermarkt.com

---

## 📝 Development Timeline

- **Week 1:** Data collection + cleaning ← WE ARE HERE
- **Week 2:** Feature engineering
- **Week 3:** Model training
- **Week 4:** Backtesting + validation
- **Week 5:** Live predictions (paper trading)
- **Week 6+:** Expand to real money

---

## ⚠️ Important Notes

1. **Backtesting ≠ Reality**
   - Historical data can have look-ahead bias
   - Real trading will vary
   - Conservative position sizing critical

2. **Start Small**
   - Paper trade first (fake money)
   - Prove model works
   - Then start with small bets

3. **Risk Management**
   - Never bet more than 2% per game
   - Use Kelly Criterion for sizing
   - Set loss limits

---

## 🔗 Related Projects

- **sports-prediction-ai** (hackathon project) - Broader sports analysis
- **growth-onomics-playbook** (landing page) - Lead generation AI

---

## 📞 Next Steps

1. ✅ Create project structure
2. ⬜ Build data collection script
3. ⬜ Scrape historical games (2023-2025)
4. ⬜ Collect betting lines
5. ⬜ Validate data quality
6. ⬜ Engineer features
7. ⬜ Train models
8. ⬜ Backtest on 2024
9. ⬜ Generate daily predictions
10. ⬜ Paper trade (2 weeks)

---

**Last Updated:** Feb 6, 2026  
**Phase:** 1 - Data Collection  
**Status:** 🟡 Starting Now
