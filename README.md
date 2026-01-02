Startup
1. Download miniconda or anaconda
2. Create a virtual environment `conda create -n trader python=3.10`
3. Activate it `conda activate trader`
4. Install initial deps `pip install lumibot alpaca.py`
5. Install transformers and friends `pip install torch torchvision torchaudio transformers`
6. Update the API_KEY and API_SECRET with values from your Alpaca account
7. Run the bot python tradingbot.py
