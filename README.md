Download miniconda or anaconda
Create a virtual environment conda create -n trader python=3.10
Activate it conda activate trader
Install initial deps pip install lumibot alpaca.py
Install transformers and friends pip install torch torchvision torchaudio transformers
Update the API_KEY and API_SECRET with values from your Alpaca account
Run the bot python tradingbot.py
