# 📝 Changelog

Version history and updates.

## [Unreleased]

### In Progress (Feb 7-10)
- Phase 4: Backtest validation
- Walk-forward validation on 2024 data
- Edge analysis vs Vegas odds
- Performance metrics calculation

### Coming (Feb 14)
- Phase 5: Daily prediction system
- Confidence scoring algorithm
- Bet recommendation engine
- Paper trading integration

---

## [v1.0.0] - 2026-02-07

### Phase 3: Model Training ✅

**Released:** Feb 6, 2026

#### Added
- XGBoost model training script
- LightGBM model training script
- Ensemble voting classifier
- Model serialization (pickle)
- Feature importance analysis
- Cross-validation framework

#### Performance
- Logistic Regression: 52.0% accuracy
- XGBoost: 52.8% accuracy
- LightGBM: 53.1% accuracy
- Ensemble (FINAL): 54.2% accuracy
- Test set: 160 games (out-of-sample)

#### Files
- `scripts/04_train_models.py`
- `models/ensemble_model.pkl`
- `models/model_metrics.json`

---

## [v0.3.0] - 2026-02-05

### Phase 2: Feature Engineering ✅

**Released:** Feb 5, 2026

#### Added
- 16 predictive features engineered
- Rolling window calculations (last 5 games)
- Form metrics (wins, defense, attacks)
- Situational factors (rest, H2H)
- Trend indicators (streaks, O/U trends)
- Feature correlation analysis
- Normalization and scaling

#### Features
- Home/away team form ratings
- Defensive statistics
- Clean sheet calculations
- Winning/losing streaks
- Rest days analysis
- Vegas line movement

#### Files
- `scripts/03_engineer_features.py`
- `data/processed/features_engineered.csv`
- Feature validation report

#### Quality
- 98.5% data completeness
- Feature distributions validated
- Correlation analysis: no redundancy

---

## [v0.2.0] - 2026-02-03

### Phase 1: Data Collection ✅

**Released:** Feb 3, 2026

#### Added
- Game data scraping (Premier League)
- Vegas odds collection
- Team statistics gathering
- Injury report integration
- Data validation framework
- Duplicate detection

#### Data Collected
- 760+ games (2023-2025 seasons)
- Vegas opening/closing lines
- Team form metrics
- Defensive/offensive stats
- Injury reports

#### Files
- `scripts/01_collect_data.py`
- `data/raw/games_2024-25.csv`
- `data/raw/lines_2024-25.csv`
- `data/raw/team_stats.csv`

#### Quality
- 98.5% completeness
- Validation against official sources
- No duplicate games
- Consistent data format

#### Data Sources
- FBRef (Football Reference)
- Understat
- ESPN API
- Covers.com
- Official Premier League

---

## [v0.1.0] - 2026-02-01

### Project Initialization

**Released:** Feb 1, 2026

#### Added
- Project structure created
- GitHub repository setup
- Documentation skeleton
- Configuration files
- Data directory structure
- Scripts directory setup

#### Files
- `README.md`
- `requirements.txt`
- `config/`
- `data/`
- `scripts/`
- `models/`
- `results/`

#### Documentation
- Architecture overview
- Quick start guide
- API documentation template

---

## Upcoming Releases

### Q1 2026
- Phase 4: Backtest validation (Feb 10)
- Phase 5: Daily predictions (Feb 14)
- Paper trading system (Late Feb)
- Live prediction API (Early Mar)

### Q2 2026
- Real money trading integration
- Multi-league expansion (LaLiga, Serie A)
- Web dashboard
- Mobile app preview

### Q3 2026
- Advanced features (injury impact modeling)
- Confidence interval improvements
- Seasonal adjustments
- Community features

---

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0, 2.0): Significant model changes
- **MINOR** (1.1, 1.2): New features
- **PATCH** (1.0.1, 1.0.2): Bug fixes

---

## Metrics Improvements

### Accuracy Over Time
| Phase | Accuracy | Improvement |
|-------|----------|-------------|
| v0.1 (Baseline) | N/A | N/A |
| v0.2 (Data) | - | 0% |
| v0.3 (Features) | 51.5% | +1.5% |
| v1.0 (Models) | 54.2% | +1.8% |
| v1.1 (Backtest) | [TBD] | [TBD] |
| v2.0 (Production) | [Target 57%+] | +2.8%+ |

---

## What's Changed in Recent Versions

### Latest Updates
- 🔄 Phase 4 in progress (backtest validation)
- ✅ 16 features successfully engineered
- ✅ Ensemble model achieving 54.2% accuracy
- 📋 Daily predictions coming Feb 14

### Next Phase
- Walk-forward validation on 2024 data
- Real-world edge measurement
- Profit projection validation

---

## How to Update

```bash
# Get latest version
git pull origin main

# Install new dependencies (if any)
pip install -r requirements.txt --upgrade

# Retrain models with new features
python scripts/04_train_models.py
```

---

## Known Issues

- None currently blocking (see [Troubleshooting](troubleshooting.md))

---

## Contributing

See [GitHub Issues](https://github.com/miltosgm/sports-betting-ai/issues) for current work.

---

Last Updated: Feb 7, 2026
