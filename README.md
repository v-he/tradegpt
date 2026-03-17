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

### Configure Alpaca credentials (PowerShell)

This project reads credentials from environment variables (do **not** hard-code keys in source).

```powershell
$env:ALPACA_API_KEY = "YOUR_ALPACA_KEY"
$env:ALPACA_API_SECRET = "YOUR_ALPACA_SECRET"
# Optional (defaults to paper):
$env:ALPACA_BASE_URL = "https://paper-api.alpaca.markets/v2"
```

### Run

#### Backtest (default)

```bash
python tradingbot.py
```

#### Live trading (optional)

Edit `tradingbot.py` and switch the entrypoint from `run_backtest()` to `run_live()`:

```python
if __name__ == "__main__":
    run_live()
```

Then run:

```bash
python tradingbot.py
```

### Notes
- `finbert_utils.py` loads a DeBERTa sentiment model from Hugging Face; the first run may download model weights.
- If you want the environment variables to persist across new terminals, set them in Windows “Environment Variables” or your PowerShell profile.
