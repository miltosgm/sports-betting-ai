# 💰 Bet Recommendations

How daily bet recommendations are generated.

**Status:** 📋 COMING SOON (Phase 5, Feb 14)

---

## Overview

Each day, model generates 5-7 bet recommendations based on:
1. Model confidence (65%+)
2. Mathematical edge vs Vegas
3. Optimal bet sizing
4. Risk management rules

---

## Recommendation Format

```
Game: Manchester City vs Chelsea
Time: 15:00 GMT
═══════════════════════════════
Model Prediction: Manchester City -1.5
Confidence: 71%
Vegas Line: City -130 (implied 56.5%)
Our Edge: +2.1%
═══════════════════════════════
Bankroll: $10,000
Recommended Bet: $150 (1.5%)
Expected Profit: $3.15
═══════════════════════════════
Kelly Criterion: 2.1% × 71% = 1.5% of bankroll
```

---

## Filtering

Recommendations only generated when:
- ✓ Confidence ≥ 65%
- ✓ Edge > 0% vs Vegas
- ✓ Data quality ≥ 95%
- ✓ Less than 2% bankroll risk

---

Detailed framework coming Feb 14.
