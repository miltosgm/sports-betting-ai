# 📦 Installation

Detailed setup instructions for different environments.

## Requirements

- **Python:** 3.9 or higher
- **Disk Space:** ~2GB for data
- **RAM:** 4GB minimum (8GB recommended)
- **OS:** macOS, Linux, or Windows

---

## Option 1: Basic Installation (Recommended)

### 1. Clone Repository
```bash
git clone https://github.com/miltosgm/sports-betting-ai.git
cd sports-betting-ai
```

### 2. Create Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import pandas; import xgboost; import lightgbm; print('✓ All dependencies installed')"
```

---

## Option 2: Docker (Advanced)

If you have Docker installed:

```bash
# Build image
docker build -t sports-betting-ai .

# Run container
docker run -it -v $(pwd)/data:/workspace/data sports-betting-ai
```

---

## Option 3: Conda Environment

If you prefer conda:

```bash
conda create -n betting-ai python=3.9
conda activate betting-ai
pip install -r requirements.txt
```

---

## Dependency Details

**Core Libraries:**
- `pandas` — Data manipulation
- `numpy` — Numerical computing
- `scikit-learn` — ML algorithms & preprocessing
- `xgboost` — Gradient boosting
- `lightgbm` — Fast gradient boosting
- `requests` — API calls
- `beautifulsoup4` — Web scraping

**Data Sources:**
- `yfinance` — Financial data (if using)
- `espn-api` — ESPN data access

**Visualization:**
- `matplotlib` — Plotting
- `plotly` — Interactive charts

**Development:**
- `jupyter` — Notebooks
- `pytest` — Testing

Full list in `requirements.txt`

---

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'xgboost'`

**Solution:**
```bash
pip install --force-reinstall xgboost
```

### Issue: `pip install` hangs

**Solution:**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

### Issue: On Windows - Command not found

**Solution:** Use `python` instead of `python3`:
```bash
python -m venv venv
python scripts/01_collect_data.py
```

### Issue: Data download fails

**Solution:** Check internet connection and verify APIs are accessible:
```bash
python scripts/01_collect_data.py --test
```

### Issue: Memory error during training

**Solution:** Reduce batch size or dataset:
```bash
# Edit config/model_config.yaml
batch_size: 32  # Reduce from 64
```

---

## Verify Everything Works

Run the test script:

```bash
python scripts/test_setup.py
```

Expected output:
```
✓ Python version: 3.9.x
✓ Dependencies loaded
✓ Data folder structure OK
✓ Models folder accessible
✓ Ready to train!
```

---

## Next Steps

After successful installation:

1. Read [Quick Start](quickstart.md)
2. Run Phase 1: `python scripts/01_collect_data.py`
3. See [Architecture](architecture.md) to understand the pipeline

---

## Get Help

If installation fails:
1. Check the [Troubleshooting](troubleshooting.md) guide
2. Open an issue on [GitHub](https://github.com/miltosgm/sports-betting-ai/issues)

Good luck! 🚀
