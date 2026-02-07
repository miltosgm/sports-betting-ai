# 🔧 Phase 2: Feature Engineering

How we create predictive features from raw data.

**Status:** ✅ COMPLETE (Feb 5, 2026)

---

## What We Do

Transform raw game data into 16 predictive features that the model can learn from.

```
Raw Data (Games, Stats, Odds)
    ↓
Feature Calculation (rolling averages, form metrics, etc.)
    ↓
16 Engineered Features
    ↓
Ready for Model Training
```

---

## The 16 Features

### Form Metrics (4)
- Home team wins (last 5 games)
- Away team wins (last 5 games)
- Home team form rating
- Away team form rating

### Defensive Metrics (4)
- Home team defensive rating
- Away team defensive rating
- Home clean sheets (last 5)
- Away goals conceded (last 5)

### Situational Factors (4)
- Home field advantage
- Head-to-head advantage
- Rest days (home team)
- Rest days (away team)

### Trend Indicators (4)
- Home winning streak
- Away losing streak
- Over/under trend (last 5)
- Vegas line movement

---

## Feature Importance

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | Home form (last 5) | 18.3% |
| 2 | Away defense rating | 15.7% |
| 3 | Head-to-head | 12.4% |
| 4 | Winning streak | 11.2% |
| 5 | Home advantage | 9.8% |

Top 5 features drive 59% of predictions.

---

## Quality Checks

✅ No missing values (100% complete)  
✅ No outliers (within expected ranges)  
✅ Low correlation (features independent)  
✅ Normalized for model training  

---

## Output

```
data/processed/
└── features_engineered.csv
    (760 games × 16 features + target)
```

---

See [Quick Start](quickstart.md) to run: `python scripts/03_engineer_features.py`

Full details: [Features](features.md)
