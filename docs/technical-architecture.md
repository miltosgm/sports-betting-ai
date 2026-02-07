# 🏗️ Technical Architecture

Low-level system design and API reference.

**Status:** 📋 ADVANCED (Coming soon)

---

## Core Components

### 1. Data Pipeline
```
API Sources → Validation → Cleaning → Storage
   ↓              ↓             ↓         ↓
FBRef      Check nulls   Dedup rows   CSV files
ESPN       Type check    Normalize    Database
Covers     Range check   Format       Cache
```

### 2. Feature Engineering
```
Raw Data → Feature Calc → Scaling → Feature Store
   ↓          ↓            ↓          ↓
Games     Rolling avg   Normalize  engineered.csv
Stats     Form metrics  StandardScaler
Odds      Situational   MinMaxScaler
```

### 3. Model Pipeline
```
Features → Preprocessing → Training → Ensemble → Predictions
   ↓            ↓             ↓          ↓          ↓
Import      Encode cats   XGBoost    Vote       Confidence
Normalize   Handle NaN    LightGBM   Average    Ranking
Split       Feature sel   Val metrics Persist    Export
```

---

## Class Hierarchy (Simplified)

```
DataCollector
├─ FBRefCollector
├─ UnderstatCollector
└─ CoversCollector

FeatureEngineer
├─ FormFeatures
├─ DefensiveFeatures
├─ SituationalFeatures
└─ TrendFeatures

ModelEnsemble
├─ XGBoostModel
├─ LightGBMModel
└─ VotingClassifier

Predictor
├─ DailyPredictor
├─ ConfidenceScorer
└─ BetRecommender
```

---

## API Reference

### Get Daily Predictions

```python
from sports_betting_ai import Predictor

predictor = Predictor()
predictions = predictor.predict_today()

# Returns:
# [
#   {
#     "game": "Arsenal vs Liverpool",
#     "prediction": "Home Win",
#     "confidence": 0.72,
#     "edge": 0.021,
#     "bet_size": 150,
#     "expected_profit": 3.15
#   },
#   ...
# ]
```

---

Full technical docs coming in v1.1
