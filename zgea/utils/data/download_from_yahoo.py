import yfinance
import pandas as pd
from typing import Optional
from typeguard import typechecked

from utils.math import to_float, calc_returns, calc_growth, reindex_and_fill


@typechecked()
def download_from_yahoo(ticker: str, name: Optional[str] = None, adjust: bool = True, dividends: bool = False) -> pd.Series:
    """
    Download from yahoo, handled with yfinance.

    :param ticker: str, ID of yfinance results
    :param name: Optional[str], name that is to be given to the data column
    :param adjust: bool, 
    :param dividends: bool,  
    :return: pd.Series, financial data with datetime as index column
    """
    if name is None:
        name = ticker

    # download data via yfinance, as float type
    data = yfinance.download(
        [ticker],
        start=None,
        period='max',
        auto_adjust=adjust,
        actions=False,
        progress=False
    )['Close'].apply(to_float)

    # rename and reindex pd.Series properties
    data.name = name
    data.index = pd.to_datetime(data.index)
    data = reindex_and_fill(data, min(data.index), max(data.index), freq="D")

    # if desired, add dividends to returns
    if dividends:
        dividends = yfinance.Ticker(ticker).dividends
        value_percent = calc_returns(data, freq="D")
        for i in dividends.index:
            if i in data.index:
                value_percent[i] += dividends[i]/data[i]

        return calc_growth(value_percent, data.iloc[0])

    return data

