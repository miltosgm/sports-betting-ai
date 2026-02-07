# 🔧 Troubleshooting

Common issues and solutions.

## Installation Issues

### "ModuleNotFoundError: No module named 'xgboost'"

**Problem:** Package not installed

**Solution:**
```bash
pip install --force-reinstall xgboost lightgbm
```

---

### "pip install hangs" or freezes

**Problem:** Network timeout or package conflicts

**Solution:**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir --timeout=1000
```

---

### "Virtual environment not activating"

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

**If still fails:**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Data Collection Issues

### "Data download fails" or "API connection error"

**Cause:** Network, rate limiting, or API down

**Solution:**
```bash
# Check internet
ping google.com

# Test individual APIs
python scripts/test_apis.py

# Retry with proxy if needed
```

---

### "Data validation fails" (98% → 85% completeness)

**Cause:** Missing data from sources

**Solution:**
```bash
# Check what's missing
python scripts/01_collect_data.py --validate

# Use cached data if available
python scripts/01_collect_data.py --use-cache
```

---

### "Duplicate games in dataset"

**Cause:** Data source returning duplicates

**Solution:**
```bash
# Clean duplicates
python scripts/02_clean_data.py --remove-duplicates
```

---

## Feature Engineering Issues

### "Features not calculated" or all NaN values

**Cause:** Data preprocessing error

**Solution:**
```bash
# Verify raw data
python scripts/check_data.py data/raw/games_2024-25.csv

# Re-run feature engineering
python scripts/03_engineer_features.py --verbose
```

---

### "Feature scaling error"

**Cause:** Features out of expected range

**Solution:**
```bash
# Check feature statistics
python scripts/analyze_features.py

# Re-scale manually
python scripts/03_engineer_features.py --rescale
```

---

## Model Training Issues

### "Out of memory" error during training

**Problem:** Dataset too large, not enough RAM

**Solution:**
```bash
# Option 1: Increase available RAM
# Close other apps, increase swap space

# Option 2: Reduce batch size
# Edit config/model_config.yaml
batch_size: 32  # from 64

# Option 3: Reduce dataset size
# Limit to recent 2 seasons instead of 5
python scripts/04_train_models.py --season 2024 2025
```

---

### "Model training takes too long" (>30 min)

**Solution:**
```bash
# Use faster model config
python scripts/04_train_models.py --fast

# Or limit features
python scripts/04_train_models.py --features 1-8
```

---

### "Model accuracy is 50%" (not 54%)

**Possible causes:**
1. Different data than docs
2. Features not normalized
3. Class imbalance not addressed

**Solution:**
```bash
# Regenerate features from scratch
rm -rf data/processed/
python scripts/03_engineer_features.py

# Retrain models
python scripts/04_train_models.py --verbose
```

---

## Prediction Issues

### "Predictions fail" or "Model file not found"

**Solution:**
```bash
# Verify model exists
ls models/ensemble_model.pkl

# If missing, retrain
python scripts/04_train_models.py
```

---

### "Predictions output is garbage"

**Cause:** Bad features for today's games

**Solution:**
```bash
# Verify today's data quality
python scripts/check_data.py --date TODAY

# Manually verify features
python scripts/debug_features.py
```

---

## System Issues

### "Python command not found"

**Solution:**

On macOS/Linux:
```bash
python3 --version  # Use python3, not python
alias python=python3  # Add to ~/.bashrc or ~/.zshrc
```

On Windows:
```bash
python --version  # python not python3
```

---

### "Permission denied" error

**Solution:**
```bash
# Add execute permission
chmod +x scripts/*.py

# Or run with explicit python
python scripts/01_collect_data.py
```

---

### "Too many files open" error

**Solution:**
```bash
# Increase file limit (macOS/Linux)
ulimit -n 4096
```

---

## Data Issues

### "Old data causing wrong predictions"

**Solution:**
```bash
# Clear cache and redownload
rm -rf data/
python scripts/01_collect_data.py --fresh
```

---

### "Feature values are extreme (too high/low)"

**Solution:**
```bash
# Normalize features
python scripts/03_engineer_features.py --normalize
```

---

## Debugging

### "General: I don't know what's wrong"

**Run diagnostics:**
```bash
python scripts/test_setup.py
```

This checks:
- ✓ Python version
- ✓ Dependencies installed
- ✓ Data folder structure
- ✓ Models accessible
- ✓ APIs reachable

---

## Still Stuck?

1. Check [FAQ](faq.md)
2. Search [GitHub Issues](https://github.com/miltosgm/sports-betting-ai/issues)
3. Open a new issue with:
   - Error message (full stack trace)
   - What you were doing
   - Your system (OS, Python version)
   - Output of `python scripts/test_setup.py`

Good luck! 🚀
