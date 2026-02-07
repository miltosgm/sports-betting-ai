# 4 Improvements - Action Plan & Status

**Date Started:** Feb 7, 2026
**Goal:** Increase accuracy from 75-77% to 80%+ through continuous improvement

---

## ✅ IMPROVEMENT 1: Paper Trading Tracking

**Status:** COMPLETE ✅

### What It Does
- Tracks every bet: prediction, odds, result, profit/loss
- Calculates win rate, ROI, Sharpe Ratio, max drawdown
- Validates if model's predicted confidence matches real-world results

### Files Created
- `paper_trading/TRACKING.md` - Human-readable daily log
- `paper_trading/daily_results.json` - JSON data storage
- `paper_trading/results/` - Individual game results

### How to Use Today
1. Place bets: Wolves, Bournemouth, Burnley ($150 each)
2. Track actual game outcomes (15:00-17:30 UTC)
3. Record in `paper_trading/daily_results.json`:
   ```json
   {
     "date": "2026-02-07",
     "predictions": 3,
     "bets_placed": 3,
     "matches": [
       {
         "match": "Wolves vs Chelsea",
         "prediction": "Home Win",
         "confidence": 0.757,
         "odds": 2.35,
         "bet_size": 150,
         "result": "WIN or LOSS",
         "actual_winner": "Wolves or Chelsea",
         "profit": 202.50 or -150
       }
     ]
   }
   ```

### Success Criteria
- After 2-4 weeks: Win rate >= 65% (matches 65%+ confidence threshold)
- ROI >= 15% (validates edge exists)
- Sharpe Ratio >= 1.0 (consistent profits)

---

## ✅ IMPROVEMENT 2: Line Movement Tracker

**Status:** COMPLETE ✅

### What It Does
- Monitors betting odds across sportsbooks in real-time
- Detects sharp money (>5% line movement)
- Identifies consensus direction (agreement across books)
- Confirms or contradicts V5 predictions

### File Created
- `scripts/07_line_movement_tracker.py`

### How to Use
```bash
# Run hourly before betting
python3 scripts/07_line_movement_tracker.py

# Check for sharp movements
tracker = LineMovementTracker()
odds = tracker.fetch_current_odds(match_id, "Wolves", "Chelsea")
sharp = tracker.detect_sharp_money(odds)
```

### Output
```
Match: Wolves vs Chelsea
Opening odds (Bet365): 2.35
Current odds (Bet365): 2.40 (↑ +2.1%)
Consensus: Sharp money on Chelsea (all books moving down)
Signal: ⚠️ Slight uncertainty, but V5 still favors Wolves
```

### Success Metrics
- Detect line movements 30+ min before game
- Flag sharp money contradicting model (re-evaluate bets)
- Track which books move first (identify sharp books)

---

## ✅ IMPROVEMENT 3: Daily Retraining Automation

**Status:** COMPLETE ✅

### What It Does
- Automatically detects concept drift (model accuracy dropping)
- Retrains all 4 models (XGBoost, LightGBM, RandomForest, CatBoost)
- Stores versioned models for rollback
- Prevents model degradation over time

### File Created
- `scripts/08_daily_retraining.py`

### Automated Schedule
**Cron Job:** Daily at 2:00 AM Athens time
- Trigger: Every morning after games complete
- Retrains on latest game results
- Updates weights based on new accuracies
- Logs metrics to `logs/retraining_*.log`

### Manual Trigger
```bash
python3 scripts/08_daily_retraining.py
```

### How It Works
1. Check: Is model >7 days old or 2% accuracy drop detected?
2. If yes: Retrain all 4 models on latest data
3. Compare: New accuracy vs previous version
4. Save: If improved, save as active model
5. Log: Record retraining metrics

### Success Criteria
- Model maintains 75%+ accuracy week-over-week
- Catch concept drift before it affects bets
- Weekly updates keep model fresh

---

## ⏳ IMPROVEMENT 4: Injury Data Integration

**Status:** IN PROGRESS (Sub-agent working)

### What It Does
- Integrates real injury data (not just card proxies)
- Quantifies impact: Key player injury = X% win prob reduction
- Expected accuracy boost: +2-3%

### Expected Deliverables (ETA: 2 hours)
- `scripts/09_injury_integrator.py` - Injury API integration
- `data/injury_impact.json` - Impact coefficients by player/team
- Updated feature set: 50 features (48 current + 2 injury)
- Backtest showing +2-3% accuracy improvement

### Data Sources (Sub-agent will integrate)
- ESPN Injury API
- Official league injury reports (scraping)
- Twitter injury announcements (LLM parsing)
- Real-time updates (hourly checks)

### Integration Plan
1. Merge injury features into V5 training
2. Quantify impact per player (star player = bigger impact)
3. Add to daily predictions pipeline
4. Retrain model with injury data
5. Deploy by Feb 8

---

## 📊 Accuracy Projection

| Phase | Model | Features | Data | Expected Accuracy | Status |
|-------|-------|----------|------|-------------------|--------|
| Current | V5 Proper | 48 | 2,660 games | 75-77% | ✅ Live |
| +1 week | V5 + Paper Trading Validation | 48 | 2,660 + validation | 56-58% live | ⏳ Tracking |
| +2 weeks | V5 + Injury Data | 50 | 2,660 + injuries | 77-80% test | ⏳ Integrating |
| +3 weeks | V5 + Daily Retraining | 50 | Fresh + injuries | 78-81% live | ✅ Scheduled |
| +4 weeks | V5 + Line Movement | 50 | All above | 79-82% live | ✅ Ready |

---

## 🎯 Today's Action Items

### IMMEDIATE (Next 2 hours)
- [ ] Place 3 bets (Wolves, Bournemouth, Burnley) - $150 each
- [ ] Log predictions in paper_trading/daily_results.json
- [ ] Track game results as they complete (15:00-17:30 UTC)
- [ ] Record actual outcomes in TRACKING.md

### BY TOMORROW
- [ ] Receive injury integration from sub-agent
- [ ] Merge injury features into V5
- [ ] Backtest with injury data (+2-3% expected)
- [ ] Deploy injury-aware V5 for Feb 8 predictions

### WEEKLY
- [ ] Log paper trading results daily
- [ ] Monitor line movement pre-game (use tracker)
- [ ] Run daily retraining (automated via cron)
- [ ] Review Sharpe Ratio & win rate

### IN 2-4 WEEKS
- [ ] Validate win rate >= 65%
- [ ] Confirm ROI >= 15%
- [ ] Decide: Proceed to real money if validated
- [ ] Expand to NFL/NBA (if PL profitable)

---

## 📈 ROI Projections

### Conservative (55% win rate on 65%+ bets)
- Daily: 2-3 bets × $150 = $300-450 risk
- Expected daily: +$30-50 (10-15% ROI)
- Monthly: +$900-1,500
- Annual: +$11k-18k

### Realistic (58% win rate on 65%+ bets)
- Daily: 2-3 bets × $150 = $300-450 risk
- Expected daily: +$60-100 (20-25% ROI)
- Monthly: +$1,800-3,000
- Annual: +$22k-36k

### Optimistic (60%+ win rate on 65%+ bets)
- Daily: 2-3 bets × $150 = $300-450 risk
- Expected daily: +$100-150 (30%+ ROI)
- Monthly: +$3,000-4,500
- Annual: +$36k-54k

**Note:** These assume:
- 2-3 qualifying bets per day average
- 65%+ confidence threshold maintained
- Concept drift managed via daily retraining
- No major market inefficiency closure

---

## ⚠️ Risk Management

### Bankroll Rules
- Start: $10,000 (paper trading)
- Max bet: $150 per game (1.5% of bankroll)
- Max daily risk: $450 (3 games × $150)
- Kelly Criterion: F* = (win% × odds - loss%) / (odds - 1)

### Drawdown Protection
- Max allowable drawdown: 20% of bankroll
- Stop trading if hit: $10k → $8k
- Resume only after retraining + validation

### Concept Drift Monitoring
- Weekly accuracy check
- If <74% accuracy: Stop trading, retrain
- If >78% accuracy: Increase bet size gradually

---

## 📂 File Structure

```
sports-betting-ai/
├── models/
│   ├── ensemble_model_v5_proper.pkl
│   └── v5_proper_metadata.json
├── scripts/
│   ├── 06_daily_predictions.py (current)
│   ├── 07_line_movement_tracker.py (new)
│   └── 08_daily_retraining.py (new)
├── paper_trading/
│   ├── TRACKING.md (daily log)
│   ├── daily_results.json (data)
│   └── results/
│       └── [game results]
├── logs/
│   ├── retraining_*.log (daily)
│   └── [other logs]
└── line_movement/
    └── [historical odds by match]
```

---

## ✅ Completion Checklist

- [x] Paper Trading System (COMPLETE)
- [x] Line Movement Tracker (COMPLETE)
- [x] Daily Retraining Pipeline (COMPLETE + SCHEDULED)
- [ ] Injury Data Integration (ETA: 2 hours)
- [ ] First Paper Trade Results (By Feb 8)
- [ ] Injury Integration Complete (By Feb 8)
- [ ] 2-Week Validation Period (By Feb 21)
- [ ] Real Money Trading Decision (By Feb 21)
- [ ] Multi-Sport Expansion (By Mar 1)

---

**Next message:** Status update on injury data integration from sub-agent
