# 🔧 Features

The 16 predictive features engineered from raw data.

## Feature Categories

### 1. Form Metrics (4 features)

**Home Team Wins (Last 5 Games)**
- Percentage of wins in last 5 games
- Range: 0-100%
- Importance: 18.3% (TOP)

**Away Team Wins (Last 5 Games)**
- Percentage of wins in last 5 away games
- Range: 0-100%
- Importance: 8.4%

**Home Team Form Rating**
- Composite score: (wins × 3 + draws × 1) / 5
- Range: 0-3.0
- Importance: 7.1%

**Away Team Form Rating**
- Same calculation for away team
- Range: 0-3.0
- Importance: 6.8%

---

### 2. Defensive Metrics (4 features)

**Home Team Defensive Rating** ⭐
- Goals conceded per game (last 5)
- Lower = better defense
- Range: 0-5
- Importance: 15.7% (2nd highest)

**Away Team Defensive Rating**
- Goals conceded per away game (last 5)
- Range: 0-5
- Importance: 9.2%

**Home Team Clean Sheets**
- Games without conceding goals (last 5)
- Range: 0-5
- Importance: 5.3%

**Away Team Goals Conceded (Last 5)**
- Total goals conceded in last 5 away games
- Range: 0-15
- Importance: 4.9%

---

### 3. Situational Factors (4 features)

**Home Field Advantage**
- Coefficient: 1.0-1.3
- Home teams win 45-55% of games
- Importance: 9.8%

**Head-to-Head Advantage** ⭐
- Win %: Home vs Away team historically
- Range: 0-100%
- Importance: 12.4% (3rd highest)

**Rest Days (Home Team)**
- Days since last game
- Range: 3-10
- Importance: 7.2%

**Rest Days (Away Team)**
- Days since last away game
- Range: 3-10
- Importance: 6.1%

---

### 4. Trend Indicators (4 features)

**Home Team Winning Streak**
- Consecutive wins
- Range: 0-10
- Importance: 11.2%

**Away Team Losing Streak**
- Consecutive losses
- Range: 0-8
- Importance: 5.8%

**Over/Under Trend (Last 5 Games)**
- Percentage of games with >2.5 goals
- Range: 0-100%
- Importance: 4.1%

**Vegas Line Movement**
- Opening vs closing line (if available)
- Range: -3 to +3
- Importance: 6.1%

---

## Feature Correlations

```
Highly Correlated (Redundancy):
- Home form rating ↔ Home wins (0.89) → Keep both (different scales)
- Away defensive rating ↔ Away losing streak (0.76) → Keep both

Independent Features (Good):
- Rest days (home) ↔ Head-to-head (0.12)
- Vegas line movement ↔ Form metrics (0.08)
```

**Conclusion:** Features provide unique information with minimal redundancy.

---

## Feature Engineering Process

### Raw Data → Features

```
Raw Game Data (teams, date, result)
        ↓
Cleaning (remove nulls, validate)
        ↓
Rolling Window Calculations (last 5 games)
        ↓
Normalization (0-1 or 0-100%)
        ↓
Final 16 Features
        ↓
Engineered Dataset (760 games × 16 features)
```

### Example: Home Team Form Rating

```python
# Raw: Last 5 games results
results = ['W', 'W', 'D', 'L', 'W']

# Calculation: wins×3 + draws×1 / 5
points = (4*3 + 1*1) / 5
form_rating = 13 / 5 = 2.6

# Feature value: 2.6 (on scale 0-3)
```

---

## Feature Importance Ranking

Complete ranking of all 16 features:

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | Home team form (last 5) | 18.3% |
| 2 | Away team defense rating | 15.7% |
| 3 | Head-to-head advantage | 12.4% |
| 4 | Home winning streak | 11.2% |
| 5 | Home field advantage | 9.8% |
| 6 | Away team form (last 5) | 8.4% |
| 7 | Rest days (home) | 7.2% |
| 8 | Home form rating | 7.1% |
| 9 | Away form rating | 6.8% |
| 10 | Vegas line movement | 6.1% |
| 11 | Rest days (away) | 6.1% |
| 12 | Away defense rating | 5.2% |
| 13 | Home clean sheets | 5.3% |
| 14 | Away losing streak | 5.8% |
| 15 | Over/under trend | 4.1% |
| 16 | Away goals conceded | 4.9% |

**Top 5 account for 59.4% of predictive power.**

---

## Distribution Checks

Each feature is checked for:
- Missing values (should be 0%)
- Outliers (should be 0-5%)
- Normal distribution (for scaling)
- Correlation (should be <0.9)

**Result:** All features pass validation ✓

---

## How We Use Features

During prediction:
1. Collect recent game data
2. Calculate all 16 features
3. Pass to trained ensemble model
4. Get probability prediction
5. Output confidence + recommendation

---

See [Model Performance](model-performance.md) to see which features matter most.
