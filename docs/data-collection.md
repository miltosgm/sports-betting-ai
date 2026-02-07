# 📊 Phase 1: Data Collection

What data we collect and from where.

**Status:** ✅ COMPLETE (Feb 3, 2026)

---

## What We Collect

### Games & Results
- Premier League game data (teams, dates, results)
- 760+ games from 2023-2025 seasons
- All match results and final scores

### Vegas Odds
- Opening lines from sportsbooks
- Closing lines
- Moneyline odds
- Point spreads

### Team Statistics
- Form metrics (wins, draws, losses)
- Defensive ratings
- Attack ratings
- Home/away performance splits

### Injury Reports
- Player availability
- Upcoming returns
- Suspensions

---

## Data Sources

| Source | Data |
|--------|------|
| FBRef (Sports Reference) | Game results, team stats |
| Understat | Advanced metrics |
| ESPN API | Games, odds |
| Covers.com | Vegas lines |
| Pinnacle | Betting odds |
| Official Premier League | Official data |

---

## Data Quality

✅ 98.5% completeness  
✅ No duplicate games  
✅ Validated against official sources  
✅ Consistent formatting  

---

## Output

```
data/raw/
├── games_2024-25.csv      (380 games)
├── lines_2024-25.csv      (Vegas odds)
├── team_stats.csv         (Team metrics)
└── injuries_current.csv   (Team news)
```

---

See [Quick Start](quickstart.md) to run: `python scripts/01_collect_data.py`
