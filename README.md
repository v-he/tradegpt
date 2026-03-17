## Setup (Windows)

### Prereqs
- Install **Miniconda** or **Anaconda**
- Create and activate a fresh environment:

```bash
conda create -n trader python=3.10 -y
conda activate trader
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure Alpaca & Polygon credentials (PowerShell)

This project reads credentials from environment variables (do **not** hard-code keys in source).

```powershell
$env:ALPACA_API_KEY = "YOUR_ALPACA_KEY"
$env:ALPACA_API_SECRET = "YOUR_ALPACA_SECRET"
# Optional (defaults to paper):
$env:ALPACA_BASE_URL = "https://paper-api.alpaca.markets/v2"

# Required for Polygon-based backtests:
$env:POLYGON_API_KEY = "YOUR_POLYGON_API_KEY"
```

### Run

#### Backtest (default)

By default `tradingbot.py` runs a Polygon‑based backtest:

```bash
python tradingbot.py
```

Make sure `POLYGON_API_KEY` is set first (see above).

#### Live trading (paper or live)

1. Edit `tradingbot.py` and switch the entrypoint from `run_backtest()` to `run_live()`:

```python
if __name__ == "__main__":
    run_live()
```

2. For **paper trading** (recommended first), keep the default base URL:

```powershell
$env:ALPACA_API_KEY = "YOUR_ALPACA_KEY"
$env:ALPACA_API_SECRET = "YOUR_ALPACA_SECRET"
$env:ALPACA_BASE_URL = "https://paper-api.alpaca.markets/v2"
```

3. For **live trading**, only change the base URL and use live keys:

```powershell
$env:ALPACA_API_KEY = "YOUR_LIVE_ALPACA_KEY"
$env:ALPACA_API_SECRET = "YOUR_LIVE_ALPACA_SECRET"
$env:ALPACA_BASE_URL = "https://api.alpaca.markets/v2"
```

4. Then start the bot:

```bash
python tradingbot.py
```

### Notes
- `finbert_utils.py` loads a DeBERTa sentiment model from Hugging Face; the first run may download model weights.
- If you want the environment variables to persist across new terminals, set them in Windows “Environment Variables” or your PowerShell profile.
- The bot does **not** currently learn or retrain itself; it uses a fixed FinBERT model and rule‑based logic. Tune parameters in `tradingbot.py` (e.g. `cash_at_risk`, take‑profit/stop‑loss levels, sentiment threshold) to change behavior.
