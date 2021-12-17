""""
Var class
"""

import yfinance as yf
import numpy as np
import datetime


class RiskMeasures:
    """
    A base class for historical Var simulation.
    """

    def __init__(self, portfolio, confidence_level=0.95):
        """
        Args:
            portfolio (obj): a Portfolio object
            confidence_level (float): the confidence level for the value at risk
        """

        self.confidence_level = confidence_level
        self.portfolio = portfolio
        self._var = None
        self._es = None

    def var(self):
        """
        Calculates the historical var cutting the return distribution at the (1-alpha) quantile
        Returns:
            float: the daily historical var
        """
        if self._var is None:
            self._var = np.quantile(self.portfolio.ret.dropna(), 1 - self.confidence_level)
        return float(self._var)

    def es(self):
        """
        Calculates the historical expected shortfall of the portfolio returns distribution
        Returns:
            float: the daily expected shortfall
        """
        if self._es is None:
            self._es = np.mean(self.portfolio.ret[self.portfolio.ret < self._var])
        return float(self._es)



class Portfolio:
    """
    A base portfolio class
    """

    def __init__(self, tickers, lookback_window=365, portfolio_weights=None):
        """
        Args:
            tickers (list): list of stock tickers in the portfolio
            portfolio_weights (list): optional, if None equally weights are assumed
        """
        self.lookback_window = lookback_window
        self.tickers = tickers
        self.portfolio_weights = portfolio_weights
        if self.portfolio_weights is not None and len(self.portfolio_weights) != len(self.tickers):
            raise ValueError("Weight vector and tickers list must have same length")
        if self.portfolio_weights is not None and sum(self.portfolio_weights) != 1:
            raise ValueError("Weights must sum to one")
        self._port_ret = None
        self._data = None

    @property
    def tickers(self):
        return self._tickers

    @tickers.setter
    def tickers(self, value):
        self._tickers = value
        self._sterilize_attr()

    @property
    def lookback_window(self):
        return self._lookback_window

    @lookback_window.setter
    def lookback_window(self, value):
        self._lookback_window = value
        self._sterilize_attr()

    @property
    def portfolio_weights(self):
        return self._portfolio_weights

    @portfolio_weights.setter
    def portfolio_weights(self, value):
        self._portfolio_weights = value
        self._sterilize_attr()

    @property
    def ret(self):
        return self._get_portfolio_return()

    def _get_data(self):
        """
        Private function to download closing prices. Do not use directly.
        Returns:
            Pandas dataframe of tickers closing price
        """
        if not isinstance(self.tickers, list):
            self.tickers = self.tickers.to_list()
        if self._data is None:
            data = yf.download(tickers=self.tickers,
                               start=datetime.datetime.today() - datetime.timedelta(days=self.lookback_window),
                               end=datetime.datetime.today(), progress=False)
            self._data = data["Adj Close"]
            if len(self._data) == 0:
                raise ValueError(f"Error during download of ticker: {self.tickers}")
            if len(self.tickers) > 1 and len(self.tickers) != len(self._data.dropna(axis=1).columns):
                miss = [tic for tic in self.tickers if tic not in self._data.dropna(axis=1).columns]
                raise ValueError(f"Error during download of ticker: {miss}")
        return self._data

    def _sterilize_attr(self):
        """
        Helper function, sterilized cached values when input data change.
        Returns:
            None
        """
        self._data = None
        self._port_ret = None

    def _get_portfolio_return(self):
        """
        Private function to calculate historical portfolio prices.
        Returns:
            Pandas time series of portfolio returns
        """
        if self._port_ret is None:
            if self.portfolio_weights is not None and not isinstance(self.portfolio_weights, list):
                self.portfolio_weights = self.portfolio_weights.to_list()
            if len(self.tickers) < 2:
                port_prices = self._get_data()
            else:
                port_weights = np.ones((len(self.tickers), 1)) / len(
                    self.tickers) if self.portfolio_weights is None else self.portfolio_weights
                port_prices = self._get_data() @ np.array(port_weights)
            self._port_ret = port_prices.pct_change(1)
        return self._port_ret


if __name__ == "__main__":
    port = Portfolio(tickers=["ENI", "AAPL"])
    risk = RiskMeasures(port)
    print(f"Var: {risk.var():.4%}, ES: {risk.es():4%}")
    risk.graph_distribution()


