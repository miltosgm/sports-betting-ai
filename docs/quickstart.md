# 🚀 Quick Start

Get up and running in 5 minutes.

## Prerequisites

- Python 3.9+
- pip or conda
- ~2GB disk space for data

## Installation

```bash
# Clone the repository
git clone https://github.com/miltosgm/sports-betting-ai.git
cd sports-betting-ai

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run the Pipeline

### Phase 1: Collect Data
```bash
python scripts/01_collect_data.py --season 2024-25
```
Downloads games, stats, and Vegas lines to `data/raw/`

### Phase 2: Engineer Features
```bash
python scripts/03_engineer_features.py
```
Creates 16 predictive features in `data/processed/`

### Phase 3: Train Models
```bash
python scripts/04_train_models.py
```
Trains XGBoost + LightGBM, creates ensemble
Output: `models/ensemble_model.pkl`

### Phase 4: Backtest (IN PROGRESS)
```bash
python scripts/05_backtest.py
```
Validates model on 2024 data
Output: `results/backtest_results.csv`

### Phase 5: Get Predictions (COMING SOON)
```bash
python scripts/06_daily_predictions.py
```
Generates daily recommendations with confidence scores

---

## What You'll See

After running Phase 3 (training), you'll get:

```
Model Training Complete!
├─ Logistic Regression: 52.0% accuracy
├─ XGBoost: 52.8% accuracy
├─ LightGBM: 53.1% accuracy
└─ Ensemble: 54.2% accuracy ✓

Ensemble model saved to: models/ensemble_model.pkl
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run Phase 1-3 (data → features → models)
3. 🔄 Wait for Phase 4 backtest results (Feb 10)
4. 📋 Phase 5 daily predictions (Feb 14)
5. 🎯 Start paper trading

---

## Troubleshooting

**Dependencies failing?**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Data not downloading?**
Check internet connection and API limits on external sources.

**Model training too slow?**
You can reduce dataset size in `config/model_config.yaml`

See [Troubleshooting](troubleshooting.md) for more help.
