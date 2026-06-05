from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional, Tuple
from alpaca_trade_api import REST
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from timedelta import Timedelta

from findebert_utils import estimate_sentiment

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")
BASE_URL = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets/v2")
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")

if not API_KEY or not API_SECRET:
    logger.warning("ALPACA_API_KEY or ALPACA_API_SECRET is not set in environment variables.")

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True,
}


TAKE_PROFIT_LONG = 1.30
STOP_LOSS_LONG = 0.90
TAKE_PROFIT_SHORT = 0.70
STOP_LOSS_SHORT = 1.10
MIN_SENTIMENT_PROB = 0.95
LOOKBACK_DAYS = 3
SLEEPTIME = "24H"


class MLTrader(Strategy):
    """Machine-learning powered sentiment strategy using Alpaca news and FinBERT."""

    def initialize(self, symbol: str = "AAPL", cash_at_risk: float = 0.8) -> None:
        self.symbol = symbol
        self.sleeptime = SLEEPTIME
        self.last_trade: Optional[str] = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def position_sizing(self) -> Tuple[float, float, int]:
        """Return (cash, last_price, quantity) based on current risk settings."""
        cash = float(self.get_cash())
        try:
            raw_last_price = self.get_last_price(self.symbol)
        except Exception:
            logger.exception("Failed to fetch last price for %s", self.symbol)
            return cash, 0.0, 0

        if raw_last_price is None:
            logger.warning("No last price available for %s (data provider returned None)", self.symbol)
            return cash, 0.0, 0

        last_price = float(raw_last_price)

        if last_price <= 0 or cash <= 0:
            return cash, last_price, 0

        quantity = int(round(cash * self.cash_at_risk / last_price, 0))
        return cash, last_price, quantity

    def get_dates(self) -> Tuple[str, str]:
        """Return (today, lookback_start) date strings for news queries."""
        today = self.get_datetime()
        lookback_start = today - Timedelta(days=LOOKBACK_DAYS)
        return today.strftime("%Y-%m-%d"), lookback_start.strftime("%Y-%m-%d")

    def get_sentiment(self) -> Optional[Tuple[float, str]]:
        """Return (probability, sentiment) or None if sentiment can't be computed."""
        today, lookback_start = self.get_dates()
        news_events = self.api.get_news(symbol=self.symbol, start=lookback_start, end=today)

        headlines = []
        for event in news_events:
            raw = getattr(event, "_raw", None) or getattr(event, "__dict__", {}).get("_raw")
            headline = raw.get("headline") if isinstance(raw, dict) else None
            if headline:
                headlines.append(headline)

        if not headlines:
            logger.info("No news found for %s between %s and %s", self.symbol, lookback_start, today)
            return None

        probability, sentiment = estimate_sentiment(headlines)
        return probability, sentiment

    def on_trading_iteration(self) -> None:
        cash, last_price, quantity = self.position_sizing()
        if last_price <= 0 or quantity <= 0:
            return
        sentiment_result = self.get_sentiment()

        if sentiment_result is None:
            return

        if quantity <= 0 or cash <= last_price:
            return

        probability, sentiment = sentiment_result

        if sentiment == "positive" and probability > MIN_SENTIMENT_PROB:
            if self.last_trade == "sell":
                self.sell_all()
            self._open_long(quantity, last_price)
        elif sentiment == "negative" and probability > MIN_SENTIMENT_PROB:
            if self.last_trade == "buy":
                self.sell_all()
            self._open_short(quantity, last_price)

    # ------------------------------------------------------------------
    # Order helpers
    # ------------------------------------------------------------------

    def _open_long(self, quantity: int, last_price: float) -> None:
        order = self.create_order(
            self.symbol,
            quantity,
            "buy",
            type="bracket",
            take_profit_price=last_price * TAKE_PROFIT_LONG,
            stop_loss_price=last_price * STOP_LOSS_LONG,
        )
        self.submit_order(order)
        self.last_trade = "buy"

    def _open_short(self, quantity: int, last_price: float) -> None:
        order = self.create_order(
            self.symbol,
            quantity,
            "sell",
            type="bracket",
            take_profit_price=last_price * TAKE_PROFIT_SHORT,
            stop_loss_price=last_price * STOP_LOSS_SHORT,
        )
        self.submit_order(order)
        self.last_trade = "sell"

    # ------------------------------------------------------------------
    # Stats / benchmark handling
    # ------------------------------------------------------------------

    def _dump_stats(self) -> None:  # type: ignore[override]
        """Safely dump stats/tearsheet, skipping benchmark failures."""
        try:
            super()._dump_stats()
        except Exception:
            logger.exception("Skipping benchmark stats/tearsheet due to upstream data error.")


def run_backtest() -> None:
    """Run a simple backtest for the MLTrader strategy."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 1, 1)

    broker = Alpaca(ALPACA_CREDS)
    strategy = MLTrader(
        name="mlstrat",
        broker=broker,
        parameters={
            "symbol": "AAPL",
            "cash_at_risk": 0.5,
        },
    )

    strategy.backtest(
        PolygonDataBacktesting,
        start_date,
        end_date,
        parameters={
            "symbol": "AAPL",
            "cash_at_risk": 0.5,
        },
        api_key=POLYGON_API_KEY,
    )


def run_live() -> None:
    """Run the strategy live using Trader."""
    broker = Alpaca(ALPACA_CREDS)
    strategy = MLTrader(
        name="mlstrat",
        broker=broker,
        parameters={
            "symbol": "AAPL",
            "cash_at_risk": 0.5,
        },
    )

    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()


if __name__ == "__main__":
    # By default, run the backtest. Switch to run_live() when ready.
    run_backtest()
