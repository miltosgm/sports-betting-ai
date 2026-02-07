# 📈 Confidence Scoring

How prediction confidence is calculated and validated.

**Status:** 📋 COMING SOON (Phase 5, Feb 14)

---

## Overview

Each prediction includes a confidence score (0-100%) representing model certainty.

### How It Works

The ensemble model outputs:
- **Prediction:** Home Win / Draw / Away Win
- **Probability:** Likelihood for each outcome
- **Confidence:** Our top prediction's probability

### Example

```
Game: Arsenal vs Liverpool

Model outputs:
├─ Home Win: 72% ← Highest
├─ Draw: 18%
└─ Away Win: 10%

Confidence: 72%
Prediction: Home Win ✓
```

---

## Confidence Calibration

We validate that confidence matches reality:

| Confidence | Actual Win Rate |
|-----------|-----------------|
| 55-60% | ~57% |
| 60-65% | ~62% |
| 65-70% | ~65% |
| 70-75% | ~74% |

✓ Well-calibrated = confidence = actual accuracy

---

## Using Confidence

**Filter Strategy:**
- Only bet 65%+ confidence predictions
- Reduces bets from 10-15 to 5-7 per day
- Increases win rate from 54% to 57-60%

---

Detailed algorithms coming Feb 14.
