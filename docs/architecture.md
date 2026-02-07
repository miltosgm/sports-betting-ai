# 🏗️ Architecture

How the model works from data to predictions.

## Pipeline Overview

```
Raw Data (Games, Stats, Odds)
        ↓
  [Data Collection]
        ↓
Clean Data (760 games)
        ↓
[Feature Engineering]
        ↓
16 Predictive Features
        ↓
[Model Training]
    ├─ XGBoost
    ├─ LightGBM
    └─ Ensemble (Voting)
        ↓
Trained Model (54.2% accuracy)
        ↓
[Backtesting]
        ↓
Edge Analysis & Profit Projections
        ↓
[Daily Predictions]
        ↓
5-7 High-Confidence Bets
```

---

## Phase 1: Data Collection

**What it does:**
- Scrapes Premier League game data (teams, dates, results)
- Collects Vegas opening lines and closing lines
- Gets team statistics (form, defense, attack, etc.)
- Fetches injury reports and team news

**Data sources:**
- FBRef (Sports Reference)
- Understat
- ESPN API
- Covers.com / Pinnacle (betting odds)
- Official Premier League website

**Output:**
```
data/raw/
├── games_2024-25.csv          (380 games)
├── lines_2024-25.csv          (Vegas odds)
├── team_stats_2024-25.csv     (Form, defense, attack)
└── injuries_current.csv        (Team news)
```

---

## Phase 2: Feature Engineering

**16 Predictive Features Created:**

**Form Metrics (4 features)**
- Home team wins (last 5 games)
- Away team wins (last 5 games)
- Home team form rating
- Away team form rating

**Defensive Metrics (4 features)**
- Home team defensive rating
- Away team defensive rating
- Home team clean sheets (last 5)
- Away team goals conceded (last 5)

**Situational Factors (4 features)**
- Home field advantage factor
- Recent head-to-head performance
- Rest days (home team)
- Rest days (away team)

**Trend Indicators (4 features)**
- Home team winning streak
- Away team losing streak
- Over/under trend (last 5 games)
- Vegas line movement (if available)

**Output:**
```
data/processed/features_engineered.csv
- 760 rows (games)
- 16 columns (features)
- 1 target (result: Home Win, Draw, Away Win)
```

---

## Phase 3: Model Training

**Three Models Trained:**

### 1. Logistic Regression (Baseline)
- Simple linear model
- Accuracy: 52.0%
- Role: Baseline comparison

### 2. XGBoost
- Gradient boosting trees
- Accuracy: 52.8%
- Fast, interpretable feature importance

### 3. LightGBM
- Lightweight gradient boosting
- Accuracy: 53.1%
- Fastest training

### 4. Ensemble (Final)
- Voting classifier (XGBoost + LightGBM)
- Accuracy: 54.2% ← **BEST**
- Combines strengths of both

**Training process:**
1. Split data: 600 games (training) + 160 games (test)
2. No data leakage (test games are sequential, not random)
3. Class weighting for imbalanced data
4. Cross-validation for stability

**Model stored:**
```
models/ensemble_model.pkl
models/model_metrics.json
```

---

## Phase 4: Backtesting

**Walk-Forward Validation:**
- Test on 2024 season (100 unseen games)
- Simulates real trading
- Measures actual profit/loss vs Vegas odds

**What we measure:**
- Win rate vs 52.4% needed
- Edge (profit margin per $1 bet)
- Maximum drawdown
- Consistency over time

**Output:**
```
results/backtest_results.csv
├── Date
├── Prediction (Home Win / Draw / Away Win)
├── Confidence
├── Vegas Line
├── Actual Result
├── Profit/Loss
└── Cumulative Profit
```

---

## Phase 5: Daily Predictions

**How it works:**

1. **Get today's games** (from Premier League API)
2. **Engineer features** (apply same transformation as training)
3. **Run model** (ensemble prediction + probability)
4. **Filter by confidence** (only 65%+ predictions)
5. **Calculate edge** (prediction prob vs Vegas line probability)
6. **Rank by value** (highest edge first)
7. **Output top bets** (5-7 recommendations)

**Each prediction includes:**
- Game details (home vs away, time)
- Model confidence (55-75%)
- Vegas line (from top sportsbooks)
- Expected value (+10% to +30%)
- Recommended bet size (Kelly Criterion)

**Output:**
```
results/daily_predictions.csv
├── Date
├── Game
├── Model Prediction
├── Confidence
├── Vegas Line
├── EV (Expected Value)
├── Recommended Bet
└── Expected Profit
```

---

## Data Flow

```
Games & Stats ──→ Data Validation ──→ Feature Engineering
                                            ↓
                                    Engineered Features
                                            ↓
                                    ┌─ XGBoost ─┐
                                    │           ├─ Ensemble ─→ Trained Model
                                    └─ LightGBM ┘
                                            ↓
                                    Historical Backtesting
                                            ↓
                            ✅ Validates Model Works
                                            ↓
                                    Daily Predictions
                                            ↓
                                    Confidence Filter
                                            ↓
                                    5-7 High-Value Bets
```

---

## Key Design Decisions

✅ **Ensemble approach** — Two models catch what one misses
✅ **Confidence filtering** — Only bet high-confidence predictions
✅ **Walk-forward validation** — No look-ahead bias
✅ **Edge-based ranking** — Bet where we have actual mathematical advantage
✅ **Conservative bet sizing** — Maximum 2% risk per game

---

See [Features](features.md) for detailed feature definitions.
