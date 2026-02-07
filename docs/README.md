# ⚽ Sports Betting AI - Premier League

Machine Learning model for high-confidence Premier League predictions.

**Status:** 🟢 Phase 4 - Backtesting (IN PROGRESS)

---

## 🎯 The Model

Selective betting system: **5-7 high-confidence bets per day** at 65%+ confidence.

- **Input:** Premier League games (daily)
- **Output:** Predictions with edge analysis
- **Target:** 57%+ win rate
- **Expected Profit:** $72k-96k/year (conservative)

---

## 📊 Progress

| Phase | Task | Status | Date |
|-------|------|--------|------|
| 1 | Data Collection | ✅ Complete | Feb 3 |
| 2 | Feature Engineering | ✅ Complete | Feb 5 |
| 3 | Model Training | ✅ Complete | Feb 6 |
| 4 | Backtesting | 🔄 In Progress | Feb 7-10 |
| 5 | Daily Predictions | 📋 Upcoming | Feb 14 |

---

## 💰 Projections

**Conservative (5 bets/day, 57% win rate):**
- Daily: $296
- Monthly: $5,920
- Annual: **$71,040**

**Target (7 bets/day, 60% win rate):**
- Daily: $415
- Monthly: $8,300
- Annual: **$99,600**

---

## 📂 Documentation

- **[Quick Start](quickstart.md)** — Get up and running in 5 minutes
- **[Architecture](architecture.md)** — How the model works
- **[Features](features.md)** — The 16 predictive signals
- **[Model Performance](model-performance.md)** — Accuracy & metrics
- **[Backtest Results](backtest-results.md)** — Validation on 2024 data
- **[Predictions](predictions.md)** — Daily recommendations system

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/miltosgm/sports-betting-ai.git
cd sports-betting-ai

# Install
pip install -r requirements.txt

# Run
python scripts/04_train_models.py
```

---

## 🛠️ Tech Stack

Python • XGBoost • LightGBM • Scikit-learn • Pandas • NumPy

---

## 📈 Latest Metrics

**Model Accuracy:** 54.2% (on 160 test games)  
**Best Model:** LightGBM (53.1%) + XGBoost (52.8%) Ensemble  
**Target:** 57%+ win rate with proper edge filtering

---

## ⚖️ Important Disclaimer

- Past performance ≠ future results
- Paper trade first (no real money until validated)
- Risk management is critical
- Never bet more than 2% per game

---

Last Updated: Feb 7, 2026 | Phase: 4 - Backtesting
